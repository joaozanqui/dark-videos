import json
import re
import unicodedata
import langid

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
        return ''
    
    return []

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

def sanitize(text: str) -> str:
    if isinstance(text, str):
        return (
            text.replace('\\', '\\\\')
                .replace('"', "'")
                .replace('\n', '\\n')
                .replace('\t', '\\t')
        )
    return text

def sanitize_list(items):
    for item in items:
        item = sanitize(str(item))
    return items

def sanitize_dict(variables: dict) -> dict:
    return {
        key: sanitize(value) if isinstance(value, str) else sanitize_list(value) if isinstance(value, list) else value
        for key, value in variables.items()
    }

def is_language_right(text, language):
    language_code = get_language_code(language)
    lang, _ = langid.classify(text)
    if lang != language_code:
        print(f"\t\t -Wrong language ({lang}), it must be {language}")

    return lang == language_code

def normalize(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8").lower()
    text = re.sub(r'[^\w\s]', '', text) 
    return text

def has_multiple_forbidden_terms(text):
    normalized = normalize(text)
    pattern = r'\*\*|\b(?:sub[-_\s]?)?(tema|topico|\(topic|topic\)|Topic|theme|visual)\b'
    matches = re.findall(pattern, normalized)
    
    return len(matches) > 1
    
def is_text_wrong(text, language):
    error = has_multiple_forbidden_terms(text) or not is_language_right(text, language)

    return error