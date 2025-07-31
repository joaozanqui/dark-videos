import google.generativeai as genai
from config.config import GEMINI_API_KEY, MODEL_NAME, DEFAULT_GENERATION_CONFIG
import time
import json
from typing import Optional, Dict, Any

def get_model(
    generation_config: dict | None = None,
    safety_settings: list | None = [],
    agent_instructions: str | None = None,
) -> genai.GenerativeModel | None:

    if not GEMINI_API_KEY:
        print("Gemini API Key not configured. Cannot get model.")
        return None
        
    final_generation_config = generation_config if generation_config is not None else DEFAULT_GENERATION_CONFIG
    
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=final_generation_config,
            system_instruction=agent_instructions,
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
        print(f"Error initializing Gemini model: {e}")
        return None
    
def handle_prompt(prompt_text: str = '', prompt_json: Optional[Dict[str, Any]] = None) -> Optional[str]:
    content_to_send = prompt_text
    if prompt_json:
        try:
            content_to_send = json.dumps(prompt_json, indent=2, ensure_ascii=False)
        except TypeError as e:
            print(f"Error: The provided dictionary could not be serialized to JSON. Details: {e}")
            return None
    
    if not content_to_send:
        print("Error: No prompt was provided (prompt_text and prompt_json are both empty).")
        return None

    return content_to_send  
    

def run(prompt_text: str = '', prompt_json: Optional[Dict[str, Any]] = None, gemini_model = get_model()) -> Optional[str]:
    time.sleep(10)
    if not gemini_model:
        print("Error: Gemini model is not initialized. Check API Key and config.")
        return "Error: Gemini model not initialized."
    
    prompt = handle_prompt(prompt_text, prompt_json)
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
             print(f"Gemini API call blocked. Feedback: {e.response.prompt_feedback}")
             return None
        print(f"Error during Gemini API call: {e}")
        return None