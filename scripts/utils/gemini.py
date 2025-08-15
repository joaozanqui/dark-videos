import google.generativeai as genai
from config.config import GEMINI_API_KEY, DEFAULT_GENERATION_CONFIG, MODELS_LIST
import time
import json
from typing import Optional, Dict, Any
import scripts.database as database

CURRENT_MODEL = 0

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
            model_name=MODELS_LIST[CURRENT_MODEL],
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

def new_chat(agent_prompt, history=[]):
    model = get_model(agent_instructions=agent_prompt)
    chat = model.start_chat(history=history)
    
    return chat

def goto_next_model():
    global CURRENT_MODEL
    CURRENT_MODEL += 1
    if CURRENT_MODEL >= len(MODELS_LIST):
        CURRENT_MODEL = 0
    print(f"- Gemini ERROR. Running again with model {MODELS_LIST[CURRENT_MODEL]}...")

def run(prompt_text: str = '', prompt_json: Optional[Dict[str, Any]] = None, agent_prompt = None) -> Optional[str]:
    time.sleep(10)
    model = get_model(agent_instructions=agent_prompt)

    if not model:
        print("Error: Gemini model is not initialized. Check API Key and config.")
        return "Error: Gemini model not initialized."
    
    prompt = handle_prompt(prompt_text, prompt_json)
    
    try:
        response = model.generate_content(prompt)
        database.log('last_response', response.text)
        if not response.text:
            goto_next_model()
            return run(prompt_text, prompt_json, agent_prompt)

        return response.text
    except Exception as e:
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
             print(f"Gemini API call blocked. Feedback: {e.response.prompt_feedback}")
             return None
        print(f"Error during Gemini API call: {e}")
        goto_next_model()
        return run(prompt_text, prompt_json, agent_prompt)