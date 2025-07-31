import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
PIXABAY_API_KEYS: list | None = json.loads(os.getenv("PIXABAY_API_KEYS")) if os.getenv("PIXABAY_API_KEYS") else None

MODEL_NAME = "gemini-2.0-flash"

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

if not PIXABAY_API_KEYS:
    raise ValueError("PIXABAY_API_KEYS not found in .env file or environment variables.")

try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Error configuring Gemini API: {e}")

DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 4096, 
}

CREATIVE_GENERATION_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 80,
    "max_output_tokens": 4096
}
