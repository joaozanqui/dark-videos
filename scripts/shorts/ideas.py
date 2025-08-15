import scripts.database as database
import scripts.utils.handle_text as handle_text
from scripts.shorts.utils import generate

def validate(shorts, qty):
    if len(shorts) != qty:
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

def run(video, variables):
    if video['shorts_ideas']:
        return video['shorts_ideas']

    print("\t\t- Generating Shorts Ideas...")
    try:
        ideas_str = generate(variables, file_name='shorts_ideas')
        ideas = handle_text.format_json_response(ideas_str)
        
        if not validate(ideas, variables['SHORTS_QTY']):
            print(f"\t\t\t- Shorts ideas generated with errors!\n\t\t\t- trying again...")
            return run(video, variables)
        
        ideas_with_id = set_ideas_id(ideas)
        database.update('videos', video['id'], 'shorts_ideas', ideas_with_id)

        return ideas_with_id
    except Exception as e:
        print(f"\t\t-Error to get shorts ideas: {e}")
        return run(video, variables)
