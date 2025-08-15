import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini
import scripts.database as database


def generate(variables, file_name):
    agent_prompt = database.get_prompt_template('agents', file_name, variables)
    prompt = database.get_prompt_template('build', file_name, variables)
    response = gemini.run(prompt_json=prompt, agent_prompt=agent_prompt)  
    
    return response

def get_description(full_script, idea, variables):
    variables['FULL_SCRIPT'] = handle_text.sanitize(full_script)
    variables['SHORTS_IDEA'] = handle_text.sanitize(str(idea))
    variables['SHORTS_IDEA_TITLE'] = handle_text.sanitize(idea['main_title'])
    
    prompt = database.get_prompt_template('build', 'shorts_description', variables)
    response = gemini.run(prompt_json=prompt)  
    
    return response