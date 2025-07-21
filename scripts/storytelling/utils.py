from string import Template
import json
from scripts.utils import export, sanitize_text

def build_template(variables, step, file_name):
    template_path = f"default_prompts/{step}/{file_name}.json"

    with open(template_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    template = Template(prompt_template)
    prompt_str = template.safe_substitute(variables)

    prompt_json = json.loads(prompt_str)
    
    prompt = json.dumps(prompt_json, indent=2, ensure_ascii=False)
    return prompt