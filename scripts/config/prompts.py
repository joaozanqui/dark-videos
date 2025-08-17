import scripts.database as database
import json

def run(channel_id, step):
    variables = database.channel_variables(channel_id)
    topics_prompt_str = database.get_prompt_template(step, 'topics', variables)
    script_prompt_str = database.get_prompt_template(step, 'script', variables)
    topics_prompt = json.loads(topics_prompt_str)
    script_prompt = json.loads(script_prompt_str)

    prompt_row = database.get_item('prompts', channel_id, column_to_compare='channel_id')
    topics_update = database.update('prompts', prompt_row['id'], f"{step}_topics", topics_prompt)
    scripts_update = database.update('prompts', prompt_row['id'], f"{step}_script", script_prompt)

    return (topics_update and scripts_update)
