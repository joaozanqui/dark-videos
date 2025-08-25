import google.generativeai as genai
import config.keys as keys

MODEL_NAME = "gemini-2.0-flash"

MODELS_LIST = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash"
]

if not keys.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

if not keys.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

if not keys.PIXABAY_API_KEYS:
    raise ValueError("PIXABAY_API_KEYS not found in .env file or environment variables.")

if not keys.SUPABASE_URL:
    raise ValueError("SUPABASE_URL not found in .env file or environment variables.")

if not keys.SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY not found in .env file or environment variables.")

if not keys.DEVICE:
    raise ValueError("DEVICE not found in .env file or environment variables.")

try:
    if keys.GEMINI_API_KEY:
        genai.configure(api_key=keys.GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Error configuring Gemini API: {e}")

DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192, 
}

CREATIVE_GENERATION_CONFIG = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 80,
    "max_output_tokens": 8192
}
