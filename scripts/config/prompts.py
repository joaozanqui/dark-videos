import scripts.database as database

def run(channel_id, step):
    variables = database.get_variables(channel_id)
    path = f"storage/prompts/{channel_id}/{step}/"
    
    topics_prompt = database.build_prompt(step, 'topics', variables, send_as_json=True)
    script_prompt = database.build_prompt(step, 'script', variables, send_as_json=True)

    database.export('topics', topics_prompt, format='json', path=path)
    database.export('script', script_prompt, format='json', path=path)

    return True
