from string import Template
from scripts.utils import get_variables, export
import json

def build_template(variables, step, file_name):
    template_path = f"default_prompts/{step}"
    template_file = f"{template_path}/{file_name}.json"

    with open(template_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    template = Template(prompt_template)
    prompt = template.safe_substitute(variables)

    return json.loads(prompt)

def run(channel_id, variables, step):
    variables = get_variables(channel_id)
    path = f"storage/prompts/{channel_id}/{step}/"
    
    topics_prompt = build_template(variables, step=step ,file_name='topics')
    script_prompt = build_template(variables, step=step ,file_name='script')

    export('topics', topics_prompt, format='json', path=path)
    export('script', script_prompt, format='json', path=path)

    return True
