import json
from string import Template
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini
import scripts.database as database

def create_prompt(variables, file_name):
    prompt = database.get_prompt_template(step='build',file=file_name)
    template_prompt = Template(prompt)
    
    prompt_str = template_prompt.safe_substitute(variables)
    prompt_json = json.loads(prompt_str)
    
    return prompt_json

def generate(variables, file_name, json_response=False):
    agent_prompt = database.get_prompt_template(step='agents', file=file_name)
    prompt = create_prompt(variables, file_name)
    response = gemini.run(prompt_json=prompt, agent_prompt=agent_prompt)  
    
    if json_response:
        return handle_text.format_json_response(response)

    return response

def get_description(full_script, idea, variables):
    variables['FULL_SCRIPT'] = handle_text.sanitize(full_script)
    variables['SHORTS_IDEA'] = handle_text.sanitize(str(idea))
    variables['SHORTS_IDEA_TITLE'] = handle_text.sanitize(idea['main_title'])
    
    prompt = create_prompt(variables, 'shorts_description')
    response = gemini.run(prompt_json=prompt)  
    return response