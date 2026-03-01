"""
rag_chat.py – Day 3: Enhanced with Budget Engine and Weather Integration.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from typing import List, Dict, Optional
import re

# Load environment variables from root .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# ================= Configuration =================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")

if not GROQ_API_KEY:
    print(" GROQ_API_KEY not found. Please add it to .env.")
    exit(1)
if not OPEN_WEATHER_API_KEY:
    print("OPEN_WEATHER_API_KEY not found. Weather features will be disabled.")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,

    # Set a realistic User-Agent to avoid potential blocking by the API
    default_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
)
MODEL_NAME = "llama-3.3-70b-versatile"  # or any other active model

# Load embedding model and Chroma
embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection("tourism_locations")

# Load location data for budget calculations
with open("data/processed/kenya_tourism.json", "r") as f:
    locations_data = json.load(f)
# Build lookup dictionary by lowercase name for fast access
location_lookup = {loc["name"].lower(): loc for loc in locations_data}

# Simple in-memory conversation history
conversation_history = []

# System prompt template (weather info may be injected)
SYSTEM_PROMPT = """You are a friendly Kenyan travel assistant. Provide practical travel advice.
Mention budget options when relevant. Consider weather if mentioned. Suggest transport options.
Be concise and helpful.

Relevant context from our knowledge base:
{context}

{weather_info}

Chat history:
{history}

User: {input}
Assistant:"""

# ================= Budget Engine =================

def estimate_budget(location_name: str, days: int, budget_level: str = "mid") -> Optional[str]:
    """
    Calculate estimated total cost for a trip.
    Uses data from kenya_tourism.json.
    budget_level: 'budget', 'mid', or 'luxury'.
    Returns a formatted string or None if location not found.
    """
    loc = location_lookup.get(location_name.lower())
    if not loc:
        return None

    # Get daily cost for the requested level
    daily_cost_str = loc.get("estimated_daily_cost", {}).get(budget_level, "")
    # Extract numeric value (assume it's like "KES 5000" or "5000")
    match = re.search(r'(\d+(?:,\d+)?)', daily_cost_str)
    if not match:
        return f"Daily cost information not available for {location_name}."
    daily_cost = float(match.group(1).replace(',', ''))

    # Accommodation is part of daily cost; we multiply by days
    accommodation = daily_cost * days

    # Park entry fees (if present)
    entry_fee = loc.get("entry_fee", {})
    citizen_fee_str = entry_fee.get("citizen", "")
    entry_cost = 0
    if citizen_fee_str:
        match = re.search(r'(\d+(?:,\d+)?)', citizen_fee_str)
        if match:
            entry_cost = float(match.group(1).replace(',', ''))

    # Transport – for simplicity, assume one‑way from Nairobi? 
    # We'll use the first transport option if available.
    transport_options = loc.get("transport_options", [])
    transport_cost = 0
    if transport_options and len(transport_options) > 0:
        first = transport_options[0]
        if isinstance(first, dict):
            cost_str = first.get("estimated_cost", "")
            match = re.search(r'(\d+(?:,\d+)?)', cost_str)
            if match:
                transport_cost = float(match.group(1).replace(',', ''))
    # For round trip, double it
    transport_cost *= 2

    # Activities – sum of estimated costs (optional)
    activities_cost = 0
    for act in loc.get("activities", []):
        if isinstance(act, dict):
            cost_str = act.get("estimated_cost", "")
            match = re.search(r'(\d+(?:,\d+)?)', cost_str)
            if match:
                activities_cost += float(match.group(1).replace(',', ''))

    total = accommodation + entry_cost + transport_cost + activities_cost

    # Format as KES with commas
    total_fmt = f"KES {total:,.0f}"
    breakdown = (
        f"Breakdown for {days} days at {budget_level} level:\n"
        f"- Accommodation & meals: KES {accommodation:,.0f}\n"
        f"- Park entry fees: KES {entry_cost:,.0f}\n"
        f"- Transport (round trip): KES {transport_cost:,.0f}\n"
        f"- Activities: KES {activities_cost:,.0f}\n"
        f"**Estimated total: {total_fmt}**"
    )
    return breakdown

# ================= Weather Integration =================

def get_weather(location: str, days_ahead: int = 0) -> Optional[str]:
    """
    Fetch current weather or forecast for a location.
    Returns a human‑readable summary or None if error.
    """
    if not OPEN_WEATHER_API_KEY:
        return "Weather service not configured."

    try:
        # Use 5‑day forecast endpoint (free)
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={location},KE&appid={OPEN_WEATHER_API_KEY}&units=metric"
        resp = requests.get(url)
        data = resp.json()
        if resp.status_code != 200:
            return f"Weather unavailable: {data.get('message', 'unknown error')}"

        # If days_ahead > 0, we need to pick the forecast for that day.
        # For simplicity, we'll just return today's forecast (first entry).
        forecast = data['list'][0]
        temp = forecast['main']['temp']
        desc = forecast['weather'][0]['description']
        wind = forecast['wind']['speed']
        return f"Current weather in {location}: {temp}°C, {desc}, wind {wind} m/s."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def extract_weather_intent(user_input: str) -> tuple:
    """
    Very basic intent extraction: if user mentions 'weather' or 'forecast',
    try to extract a location (last word?).
    Returns (location, days_ahead) or (None, None).
    """
    lower = user_input.lower()
    if 'weather' in lower or 'forecast' in lower or 'temperature' in lower:
        # Simple: take last word as location (improve later)
        words = user_input.split()
        if words:
            return words[-1].strip('?.,!'), 0
    return None, None

# ================= Retrieval and Generation =================

def retrieve_context(query: str, k: int = 5) -> str:
    """Retrieve top k relevant chunks from Chroma."""
    query_emb = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=k)
    docs = results['documents'][0] if results['documents'] else []
    return "\n\n".join(docs)

def call_groq(prompt: str) -> str:
    """Call the chosen model via Groq."""
    try:
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

def format_history(history: List[Dict]) -> str:
    """Format conversation history as a string."""
    lines = []
    for turn in history:
        lines.append(f"User: {turn['user']}")
        lines.append(f"Assistant: {turn['assistant']}")
    return "\n".join(lines)

# ================= Main Chat Loop =================

def main():
    print("=== Kenya Travel Assistant (Budget + Weather enabled) ===")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("How may I help you?: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # ---- Intent detection for budget ----
        # Look for keywords: budget, cost, price, plus a number (days) and a location.
        budget_response = None
        if any(word in user_input.lower() for word in ["budget", "cost", "price", "estimate"]):
            # Try to extract number of days
            days_match = re.search(r'(\d+)\s*days?', user_input.lower())
            days = int(days_match.group(1)) if days_match else None
            # Try to extract location – we'll use the last word that might be a place name
            words = user_input.split()
            # Heuristic: assume location is a word that is capitalized or after "to"/"in"
            location_candidate = None
            for i, w in enumerate(words):
                if w.lower() in ["to", "in", "at"] and i+1 < len(words):
                    location_candidate = words[i+1].strip('?.,!')
                    break
            if not location_candidate and words:
                location_candidate = words[-1].strip('?.,!')

            if days and location_candidate:
                # Determine budget level from keywords
                level = "mid"
                if "budget" in user_input.lower() or "cheap" in user_input.lower():
                    level = "budget"
                elif "luxury" in user_input.lower() or "high-end" in user_input.lower():
                    level = "luxury"

                budget_response = estimate_budget(location_candidate, days, level)
                if budget_response:
                    print(f"\n[Budget Estimate]\n{budget_response}\n")
                    # Optionally, still continue to get general advice? For now, we'll just show estimate.
                    # If you want to also retrieve context and generate a response, remove the continue.
                    # Here we just show estimate and ask for next query.
                    continue
                else:
                    print(f"No budget data for '{location_candidate}'. Continuing with general advice.\n")

        # ---- Weather intent ----
        weather_info = ""
        loc_weather, days_ahead = extract_weather_intent(user_input)
        if loc_weather:
            weather_info = get_weather(loc_weather, days_ahead)
            if weather_info:
                weather_info = f"Weather update: {weather_info}"

        # ---- Normal RAG flow ----
        context = retrieve_context(user_input)
        history = format_history(conversation_history)

        prompt = SYSTEM_PROMPT.format(
            context=context,
            weather_info=weather_info,
            history=history,
            input=user_input
        )

        print("Assistant: ", end="", flush=True)
        response = call_groq(prompt)

        # Save to history
        conversation_history.append({"user": user_input, "assistant": response})

        print(response + "\n")

if __name__ == "__main__":
    main()