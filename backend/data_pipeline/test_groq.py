import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# load_dotenv()

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],

    # Set a realistic User-Agent to avoid potential blocking by the API
    default_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
)

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)