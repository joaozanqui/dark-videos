import os
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME, DEFAULT_GENERATION_CONFIG

def export(file_name: str, data: str, format='txt', path='storage/titles/') -> str:
    try:
        os.makedirs(path, exist_ok=True)
        export_path = f"{path}{file_name}.{format}"
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(data)
        
        return export_path
    except Exception as e:
        print(f"Error exporting {file_name}: {e}")
        return None
    

def get_gemini_model(
    generation_config: dict | None = None,
    safety_settings: list | None = None
) -> genai.GenerativeModel | None:

    if not GEMINI_API_KEY:
        print("Gemini API Key not configured. Cannot get model.")
        return None
        
    final_generation_config = generation_config if generation_config is not None else DEFAULT_GENERATION_CONFIG
    
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=final_generation_config,
            safety_settings=[]
        )
        return model
    except Exception as e:
        print(f"Error initializing Gemini model: {e}")
        return None

