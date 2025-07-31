import scripts.database as database
from scripts.utils import build_template

def run(channel_id, step):
    variables = database.get_variables(channel_id)
    path = f"storage/prompts/{channel_id}/{step}/"
    
    topics_prompt = build_template(variables, step=step ,file_name='topics')
    script_prompt = build_template(variables, step=step ,file_name='script')

    database.export('topics', topics_prompt, format='json', path=path)
    database.export('script', script_prompt, format='json', path=path)

    return True
