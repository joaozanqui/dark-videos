import os
import google.generativeai as genai
from config.config import GEMINI_API_KEY, MODEL_NAME, DEFAULT_GENERATION_CONFIG
from typing import Optional, Dict, Any
import re
import json
import scripts.database as database
import scripts.sanitize as sanitize
from string import Template
import time
from pathlib import Path

ALLOWED_IMAGES_EXTENSIONS = ['jpg', 'png', 'jpeg']

def get_last_downloaded_file():
    downloads_path = Path.home() / 'Downloads'
    
    if not downloads_path.exists() or not downloads_path.is_dir():
        downloads_path = Path.home() / 'Transferências'
        if not downloads_path.exists() or not downloads_path.is_dir():
            return None
    
    files = [f for f in downloads_path.iterdir() if f.is_file() and not str(f).endswith(('.tmp', '.crdownload'))]

    if not files:
        return None

    last_file = max(files, key=os.path.getctime)
    return last_file 

def get_gemini_model(
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

def analyze_with_gemini(prompt_text: str = '', prompt_json: Optional[Dict[str, Any]] = None, gemini_model = get_gemini_model()) -> Optional[str]:
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
    


def refactor_dict(json_file):
    items = []
    for item in json_file:
        if isinstance(item, dict):
            items.append(item)
        else:
            print(f"Skipping invalid item structure: {item}")
    
    return items

def format_json_response(response):
    
    json_match = re.search(r'```json\s*([\s\S]+?)\s*```', response, re.IGNORECASE)
    if json_match:
        json_str = json_match.group(1)
    else:
        start_index = response.find('[')
        end_index = response.rfind(']')
        if start_index != -1 and end_index != -1 and end_index > start_index:
                json_str = response[start_index:end_index+1]
        else:
                json_str = response 
                
    try:
        json_file = json.loads(json_str)
        if isinstance(json_file, list): 
            refactored_dict = refactor_dict(json_file)
            return refactored_dict
        elif isinstance(json_file, dict):
            refactored_dict = refactor_dict([json_file])[0]
            return refactored_dict
        else:
            print("  - Warning: LLM response for subject was not a JSON list.")

    except Exception as e:
        print(f"\t\t\t - Error decoding JSON from subject response.: {e}") 
        print(f"\n{response}")
        return ''
    
    return []

def get_prompt(step, file_name, variables):
    sanitized_variables = sanitize.variables(variables)
    prompt_template = database.get_prompt_template(step, file_name)
    template = Template(prompt_template)
    prompt = template.safe_substitute(sanitized_variables)
    
    return prompt

def get_language_code(language_input: str) -> str | None:
    normalized_input = language_input.lower()

    if 'portugu' in normalized_input:
        return 'pt'
    elif 'english' in normalized_input or 'ingl' in normalized_input:
        return 'en'
    elif 'spanish' in normalized_input or 'espan' in normalized_input:
        return 'es'
    elif 'french' in normalized_input or 'franc' in normalized_input:
        return 'fr'
    elif 'german' in normalized_input or 'alem' in normalized_input:
        return 'de'
    
    return None

def get_allowed_expressions(channel_id, is_video=False):
    path = f"assets/expressions/{str(channel_id)}/{'chroma' if is_video else 'transparent'}"
    allowed_expressions = []
    for expression in os.listdir(path):
        full_path = os.path.join(path, expression)
        if os.path.isfile(full_path):
            allowed_expressions.append(expression.split('.')[0])
    
    return allowed_expressions

def build_template(variables, step, file_name):
    prompt_template = database.get_prompt_template(step, file_name)
    template = Template(prompt_template)

    prompt = template.safe_substitute(variables)

    prompt_json = json.loads(prompt)
    
    # na chamada em config.prompts nao tem essa linha de baixo
    prompt = json.dumps(prompt_json, indent=2, ensure_ascii=False)
    return prompt