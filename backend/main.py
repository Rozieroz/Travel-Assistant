"""
main.py – FastAPI backend for Kenya Travel Assistant.

Endpoints:
- POST /chat       – Send a message and get a reply (session‑based)
- GET  /weather    – Get current weather for a location
- POST /estimate   – Get a budget estimate for a trip
"""

import datetime
import os
import json
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# -------------------- Load environment --------------------
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in .env")

# Currency conversion (for budget estimates)
USD_TO_KES = 130  # Update this exchange rate periodically

def format_currency(kes_amount: float) -> str:
    """Format amount in both KES and USD"""
    kes_formatted = f"KES {kes_amount:,.0f}"
    usd_amount = kes_amount / USD_TO_KES
    usd_formatted = f"USD ${usd_amount:,.0f}"
    return f"{kes_formatted} (≈ {usd_formatted})"

# -------------------- Global initialisation --------------------
# Embedding model
embedder = SentenceTransformer(
    'sentence-transformers/all-MiniLM-L6-v2',
    cache_folder="/data_pipeline/cache",
)

# Chroma persistent DB (lighter memory footprint)
chroma_client = chromadb.PersistentClient(
    path="/data_pipeline/data/chroma_db",
    settings={"chroma_db_impl": "duckdb+parquet", "persist_directory": "/data_pipeline/data/chroma_db"}
)
collection = chroma_client.get_collection("tourism_locations")

# Load location data
with open("../data_pipeline/data/processed/kenya_tourism.json", "r") as f:
    locations_data = json.load(f)
location_lookup = {loc["name"].lower(): loc for loc in locations_data}

# In-memory session store (demo; use Redis in production)
sessions: Dict[str, List[Dict[str, str]]] = {}
MAX_HISTORY = 10  # Keep last 10 turns per session

# -------------------- Model info --------------------
# MODEL_NAME = "llama-3.3-70b-versatile"
# client = None  # Groq client will be lazily initialized

# Use a smaller / quantized model- for deployment
MODEL_NAME = "TheBloke/LLaMA-7B-GGUF-8bit"  
client = None  # Groq client will be lazily initialized


# Tokenizer (small, safe in memory)
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# -------------------- Pydantic models --------------------
class ChatRequest(BaseModel):
    session_id: str
    message: str
    currency: Optional[str] = "KES"

class ChatResponse(BaseModel):
    session_id: str
    reply: str

class WeatherRequest(BaseModel):
    location: str
    days: Optional[int] = 0

class WeatherResponse(BaseModel):
    location: str
    weather: str

class EstimateRequest(BaseModel):
    location: str
    days: int
    budget_level: str = "mid"

class EstimateResponse(BaseModel):
    location: str
    days: int
    budget_level: str
    estimate: str

# -------------------- Helper functions --------------------
def retrieve_context(query: str, k: int = 5) -> str:
    """Retrieve top k relevant chunks from Chroma."""
    query_emb = embedder.encode(query,
                                device='cpu',          # ensure CPU
                                show_progress_bar=False
                                ).tolist()
    
    results = collection.query(query_embeddings=[query_emb], n_results=k)
    docs = results['documents'][0] if results['documents'] else []
    return "\n\n".join(docs)

def call_groq(prompt: str) -> str:
    """Call the chosen model via Groq lazily."""
    try:
        global client
        if client is None:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=GROQ_API_KEY,
                default_headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant for Kenya."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=512,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling Groq API: {str(e)}"

def get_weather(location: str, days_ahead: int = 0) -> str:
    """Fetch current weather (or forecast) for a location."""
    if not OPEN_WEATHER_API_KEY:
        return "Weather service not configured."

    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={location},KE&appid={OPEN_WEATHER_API_KEY}&units=metric"
        resp = requests.get(url)
        data = resp.json()
        if resp.status_code != 200:
            return f"Weather unavailable: {data.get('message', 'unknown error')}"

        forecast = data['list'][0]
        temp = forecast['main']['temp']
        desc = forecast['weather'][0]['description']
        wind = forecast['wind']['speed']
        return f"Current weather in {location}: {temp}°C, {desc}, wind {wind} m/s."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def estimate_budget(location_name: str, days: int, budget_level: str = "mid", show_usd: bool = True) -> Optional[str]:
    loc = location_lookup.get(location_name.lower())
    if not loc:
        return None

    # Accommodation
    daily_cost_str = loc.get("estimated_daily_cost", {}).get(budget_level, "")
    match = re.search(r'(\d+(?:,\d+)?)', daily_cost_str)
    if not match:
        return f"Daily cost information not available for {location_name}."
    daily_cost = float(match.group(1).replace(',', ''))
    accommodation = daily_cost * days

    # Park entry fees
    entry_fee = loc.get("entry_fee", {})
    citizen_fee_str = entry_fee.get("citizen", "")
    entry_cost = 0
    if citizen_fee_str:
        match = re.search(r'(\d+(?:,\d+)?)', citizen_fee_str)
        if match:
            entry_cost = float(match.group(1).replace(',', ''))

    # Transport
    transport_options = loc.get("transport_options", [])
    transport_cost = 0
    if transport_options and len(transport_options) > 0:
        first = transport_options[0]
        if isinstance(first, dict):
            cost_str = first.get("estimated_cost", "")
            match = re.search(r'(\d+(?:,\d+)?)', cost_str)
            if match:
                transport_cost = float(match.group(1).replace(',', ''))
    transport_cost *= 2  # round trip

    # Activities
    activities_cost = 0
    for act in loc.get("activities", []):
        if isinstance(act, dict):
            cost_str = act.get("estimated_cost", "")
            match = re.search(r'(\d+(?:,\d+)?)', cost_str)
            if match:
                activities_cost += float(match.group(1).replace(',', ''))

    total = accommodation + entry_cost + transport_cost + activities_cost

    kes_total = f"KES {total:,.0f}"
    usd_total = f"USD ${total/USD_TO_KES:,.0f}"

    breakdown = (
        f"Breakdown for {days} days at {budget_level} level:\n"
        f"- Accommodation & meals: {format_currency(accommodation)}\n"
        f"- Park entry fees: {format_currency(entry_cost)}\n"
        f"- Transport (round trip): {format_currency(transport_cost)}\n"
        f"- Activities: {format_currency(activities_cost)}\n"
        f"**Estimated total: {kes_total} (≈ {usd_total})**"
    )
    return breakdown

def extract_weather_intent(user_input: str) -> tuple:
    """Simple heuristic to detect weather requests and guess location."""
    lower = user_input.lower()
    if 'weather' in lower or 'forecast' in lower or 'temperature' in lower:
        words = user_input.split()
        if words:
            return words[-1].strip('?.,!'), 0
    return None, None

# -------------------- FastAPI app --------------------
app = FastAPI(title="Kenya Travel Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("Kenya Travel Assistant API starting...")
    print(f"Loaded {len(location_lookup)} tourism locations")

@app.get("/")
def root():
    return {"message": "Kenya Travel Assistant API is running."}

@app.get("/healthz")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "Safari Scouts API"
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Process a chat message with session memory."""
    session_id = request.session_id
    user_message = request.message
    currency = request.currency  # already optional with default

    # Currency hint
    currency_hint = ""
    if currency == "USD":
        currency_hint = "Show all prices in USD. Use approximate conversion (1 USD ≈ 130 KES)."
    elif currency == "BOTH":
        currency_hint = "Show prices in both KES and USD with approximate conversion (1 USD ≈ 130 KES)."
    else:
        currency_hint = "Show prices in Kenyan Shillings (KES)."

    # Retrieve or create session
    if session_id not in sessions:
        sessions[session_id] = []
    history = sessions[session_id]

    # Weather info
    weather_info = ""
    loc_weather, _ = extract_weather_intent(user_message)
    if loc_weather:
        weather_info = get_weather(loc_weather)
        if weather_info:
            weather_info = f"Weather update: {weather_info}"

    # Retrieve context
    context = retrieve_context(user_message)

    # Format history
    history_str = "\n".join(
        f"User: {turn['user']}\nAssistant: {turn['assistant']}"
        for turn in history
    )

    # Build prompt
    prompt = f"""You are a friendly Kenyan travel assistant. Provide practical travel advice.
Mention budget options when relevant. {currency_hint} 
Consider weather if mentioned and give recommendations on clothing and gear based on weather predictions.

Ask follow‑up questions if you need more info to give a good answer. For budget questions, ask about preferred accommodation type (budget, mid-range, luxury) and activities.

Ask the user if their location is Nairobi CBD or if they need to get to CBD first, unless they specify they will use a cab.
Suggest transport options and specify from where the journey starts and where to alight. 
If the user is in Nairobi CBD or if they need to get to CBD first unless when using a cab.
If you don't know from where they need to board a matatu, don't mention it.

Remember sometimes Tourists may not about boarding matatus or locals may not be willing to board matatus.
Be concise and helpful.

Relevant context from our knowledge base:
{context}

{weather_info}

Chat history:
{history_str}

User: {user_message}
Assistant:"""

    # Get response
    reply = call_groq(prompt)

    # Save history (limit last 10)
    history.append({"user": user_message, "assistant": reply})
    if len(history) > MAX_HISTORY:
        history.pop(0)

    return ChatResponse(session_id=session_id, reply=reply)

@app.get("/weather", response_model=WeatherResponse)
def weather_endpoint(location: str, days: int = 0):
    """Get current weather for a location."""
    weather = get_weather(location, days)
    return WeatherResponse(location=location, weather=weather)

@app.post("/estimate", response_model=EstimateResponse)
def estimate_endpoint(request: EstimateRequest):
    estimate = estimate_budget(request.location, request.days, request.budget_level)
    if estimate is None:
        raise HTTPException(status_code=404, detail=f"Location '{request.location}' not found in knowledge base.")
    
    return EstimateResponse(
        location=request.location,
        days=request.days,
        budget_level=request.budget_level,
        estimate=estimate
    )

# Optional: run with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT or fallback to 8000 locally
    uvicorn.run(app, host="0.0.0.0", port=port)