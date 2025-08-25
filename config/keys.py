import os
import json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
PIXABAY_API_KEYS: list | None = json.loads(os.getenv("PIXABAY_API_KEYS")) if os.getenv("PIXABAY_API_KEYS") else None
SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY: str | None = os.getenv("SUPABASE_ANON_KEY")
DEVICE: int | None = os.getenv("DEVICE")