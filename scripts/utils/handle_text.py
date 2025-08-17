import json
import re
import scripts.utils.gemini as gemini
import unicodedata
import langid
from string import Template

def substitute_variables_in_json(data_structure, variables):
    if isinstance(data_structure, dict):
        return {k: substitute_variables_in_json(v, variables) for k, v in data_structure.items()}
    elif isinstance(data_structure, list):
        return [substitute_variables_in_json(i, variables) for i in data_structure]
    elif isinstance(data_structure, str):
        return Template(data_structure).safe_substitute(variables)
    else:
        return data_structure

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
        start_brace = response.find('{')
        start_bracket = response.find('[')

        if start_brace == -1:
            start_index = start_bracket
        elif start_bracket == -1:
            start_index = start_brace
        else:
            start_index = min(start_brace, start_bracket)

        if start_index == -1:
            json_str = response
        else:
            end_brace = response.rfind('}')
            end_bracket = response.rfind(']')
            end_index = max(end_brace, end_bracket)

            if end_index > start_index:
                json_str = response[start_index : end_index + 1]
            else:
                json_str = response

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        gemini.goto_next_model()
        return None

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