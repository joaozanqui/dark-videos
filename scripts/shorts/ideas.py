import scripts.database as database
from scripts.shorts.utils import generate

def validate(shorts):
    if len(shorts) != 5:
        return False
    
    required_fields = ['main_title', 'explanation_of_interest', 'curiosity_addressed']
    for short in shorts:
        if not all(field in short for field in required_fields):
            return False
        
    return True

def set_ideas_id(ideas):
    for id, idea in enumerate(ideas):
        idea['id'] = id+1
    
    return ideas

def run(path, variables):
    file_name = 'shorts_ideas'
    file_path = f"{path}{file_name}.json"

    if database.exists(file_path):
        return database.get_json_data(file_path)

    print("\t\t- Generating Shorts Ideas...")
    try:
        ideas = generate(variables, file_name, json_response=True)
        
        if not validate(ideas):
            print(f"\t\t\t- Shorts ideas generated with errors!\n\t\t\t- trying again...")
            return run(path, variables)
        
        ideas_with_id = set_ideas_id(ideas)
        database.export(file_name, ideas_with_id, format='json', path=path)

        return ideas_with_id
    except Exception as e:
        print(f"\t\t-Error to get shorts ideas: {e}")
        return run(path, variables)
