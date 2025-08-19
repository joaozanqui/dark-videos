import scripts.database as database
from scripts.shorts.utils import generate
import scripts.utils.handle_text as handle_text
import json

def last_shorts_number(video):
    all_shorts = database.get_data('shorts', video['id'], 'video_id')
    if not all_shorts:
        return 0
    
    sorted_shorts = sorted(all_shorts, key=lambda k: k['number'])
    return sorted_shorts[-1]['number']

def run(video, idea, variables):
    if last_shorts_number(video) >= variables['SHORTS_QTY']:
        return

    variables['SHORTS_IDEA_TITLE'] = idea['main_title']
    variables['SHORTS_IDEA'] = handle_text.sanitize(json.dumps(idea, indent=2, ensure_ascii=False))

    try:
        print(f"\t\t\t- Shorts {idea['id']}...")
        script = generate(variables, file_name='shorts_script')
        if handle_text.is_text_wrong(script, variables['LANGUAGE']):
            print(f"\t\t\t- Shorts Script generated with errors!\n\t\t\t- trying again...")
            return run(idea, variables)
        
        shorts_data = {
            "video_id": video['id'],
            "number": idea['id'],
            "full_script": script,
        }
        
        database.insert(shorts_data, 'shorts')
        return
    except Exception as e:
        print(f"\t\t-Error to get shorts script: {e}")
        return run(video, idea, variables)