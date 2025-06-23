import os
import google.generativeai as genai
from config.config import GEMINI_API_KEY, MODEL_NAME, DEFAULT_GENERATION_CONFIG
from typing import Optional
import re
import json
from string import Template
import time

def export(file_name: str, data: str, format='txt', path='storage/') -> str:
    try:
        os.makedirs(path, exist_ok=True)
        export_path = f"{path}{file_name}.{format}"
        with open(export_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                f.write(data)
        
        return export_path
    except Exception as e:
        print(f"Error exporting {file_name}: {e}")
        return None
    

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

def analyze_with_gemini(prompt_text: str, gemini_model = get_gemini_model()) -> Optional[str]:
    time.sleep(10)
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
    
def refactor_dict(json_file):
    items = []
    for item in json_file:
        if isinstance(item, dict):
            items.append(item)
        else:
            print(f"Skipping invalid item structure: {item}")

    if(len(items) == 1):
        return items[0]
    
    return items

def format_json_response(response):
    
    json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL | re.IGNORECASE)
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
            return refactor_dict(json_file)
        else:
            print("  - Warning: LLM response for subject was not a JSON list.")

    except json.JSONDecodeError:
        print(f"  - Error decoding JSON from subject response. Raw text: '{json_str[:200]}...'") 
    
    return []

def get_prompt(prompt_file, variables):
    prompt_path = f"{prompt_file}"
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    template = Template(prompt_template)
    prompt = template.safe_substitute(variables)
    
    return prompt

def get_final_language():
    with open('config/data.json', "r", encoding="utf-8") as file:
        data = json.load(file)    
    language = data['final_language']

    if not language:
        language = 'english'

    return language

def get_videos_duration():
    with open('config/data.json', "r", encoding="utf-8") as file:
        data = json.load(file)    
    duration = data['duration']

    if not duration:
        duration = 20

    return duration