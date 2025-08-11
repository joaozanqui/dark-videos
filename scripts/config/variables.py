import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini
import scripts.database as database
import json

def set_qty_variables(variables):
    variables['NUMBER_OF_DEV_TOPICS'] = 5
    variables['NUMBER_OF_SUBTOPICS_MIN'] = 3
    variables['NUMBER_OF_SUBTOPICS_MAX'] = 5
    
    return variables

def remove_variables_period(variables):
    return {
        key: value[:-1] if isinstance(value, str) and value.endswith('.') else value
        for key, value in variables.items()
    }

def all_variables_generated_properly(original_variables, generated_variables):
    generated_keys = []
    for key, value in generated_variables.items():
        if isinstance(value, list):
            return False
        generated_keys.append(key)
        
    for key, value in original_variables.items():
        if not key in generated_keys:
            return False

    return True 

def has_invalid_keys(variables):
    invalid_keys = []
    for key, value in variables.items():
        if "," in key:
            invalid_keys.append(key)

    return len(invalid_keys) > 0

def generate_variables(prompt_variables):
    prompt = database.get_prompt_template('script', 'get_variables', prompt_variables)
    prompt_json = json.loads(prompt)
    response = gemini.run(prompt_json=prompt_json)
    current_variables = handle_text.format_json_response(response)

    if not isinstance(current_variables, dict) or has_invalid_keys(current_variables) or not all_variables_generated_properly(prompt_variables['variables'], current_variables):
        print(f"\t\t- Invalid. Generating again...")
        return generate_variables(prompt_variables)
    
    return current_variables

def separate_variables_by_type(variables):
    separated_data = {}
    for var in variables:
        var_type = var.get('type')
        if var_type not in separated_data:
            separated_data[var_type] = {}
        
        separated_data[var_type].update({
            var.get('name'): var.get('description')
        })
    return separated_data

def set_variables(channel, analysis):
    all_variables = {}

    prompt_variables = {
        "channel": handle_text.sanitize(str(channel)),
        "phase1_insights": handle_text.sanitize(analysis['insights_p1']),
        "phase2_insights": handle_text.sanitize(analysis['insights_p2']),
        "phase3_insights": handle_text.sanitize(analysis['insights_p3']),
    }
    
    variables = database.get_all_data('variables')
    variables_by_type = separate_variables_by_type(variables)
    processed_variables = 0

    for variables_type, variables_from_type in variables_by_type.items():
        processed_variables += len(variables_from_type)
        print(f"\t- {processed_variables}/{len(variables)}")

        prompt_variables['variables'] = variables_from_type
        prompt_variables['type'] = variables_type
        current_variables = generate_variables(prompt_variables)
        all_variables.update(current_variables)

    if all_variables:
        variables_without_period = remove_variables_period(all_variables) 
        return set_qty_variables(variables_without_period)
    
    return {}


def build(channel, analysis):    
    print(f"- Variables...")

    language = database.get_item('languages', channel['language_id'])

    variables = set_variables(channel, analysis)
    
    if not variables:
        return run(channel, analysis)

    variables['LANGUAGE_AND_REGION'] = language['name']
    variables['VIDEO_DURATION'] = channel['videos_duration']
    
    return variables

def run(channel, analysis):
    variables = build(channel, analysis)
    
    channel_response = database.get_item('channels_responses', channel['id'], 'channel_id')
    database.update('channels_responses', channel_response['id'], 'variables', variables)

    return variables