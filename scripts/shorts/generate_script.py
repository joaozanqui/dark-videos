import scripts.database as database
from scripts.shorts.utils import generate
import scripts.utils.handle_text as handle_text
import json

def run(path, variables):
    prompt_file_name = f"shorts_script"
   
    file_name = f"shorts_{variables['SHORTS_IDEA_JSON']['id']}"
    file_path = f"{path}{file_name}.txt"
    
    variables['SHORTS_IDEA_TITLE'] = variables['SHORTS_IDEA_JSON']['main_title']
    variables['SHORTS_IDEA'] = handle_text.sanitize(json.dumps(variables['SHORTS_IDEA_JSON'], indent=2, ensure_ascii=False))

    if database.exists(file_path):
        return database.get_txt_data(file_path)
    
    try:
        print(f"\t\t\t- {file_name}...")
        script = generate(variables, prompt_file_name)
        if handle_text.is_text_wrong(script, variables['LANGUAGE']):
            print(f"\t\t\t- Shorts Script generated with errors!\n\t\t\t- trying again...")
            return run(path, variables)
        
        database.export(file_name, script, path=path)
        
        return script
    except Exception as e:
        print(f"\t\t-Error to get shorts script: {e}")
        return run(path, variables)