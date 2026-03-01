"""Configuration module for the Safari Scouts backend application.
This module loads environment variables and defines constants used across the application.
moves the reusable configuration logic to a single place, making it easier to manage and maintain.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root .env
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")