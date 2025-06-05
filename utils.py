import os
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME, DEFAULT_GENERATION_CONFIG
from typing import Optional

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

def analyze_with_gemini(prompt_text: str, gemini_model = get_gemini_model()) -> Optional[str]:
    if not gemini_model:
        print("Error: Gemini model is not initialized. Check API Key and config.")
        return "Error: Gemini model not initialized."
    try:
        response = gemini_model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
             print(f"Gemini API call blocked. Feedback: {e.response.prompt_feedback}")
             return f"Error: Content generation blocked. {e.response.prompt_feedback}"
        print(f"Error during Gemini API call: {e}")
        return f"Error processing request with Gemini: {e}"