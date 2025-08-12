import assets.main as assets
import scripts.utils.gemini as gemini
import scripts.utils.handle_text as handle_text
import scripts.database as database

def handle_description(video_data, infos_variables):
    if video_data['description']:
        return video_data['description']
    
    print(f"\t\t - Video Description...")
    prompt = database.get_prompt_template('build', 'video_description', infos_variables)
    description = gemini.run(prompt_json=prompt)
    
    database.update('videos', video_data['id'], 'description', description)
    return description

def generate_thumbnail_prompt(video_data, infos_variables, description):
    thumbnail_data = video_data['thumbnail_data']
    if not thumbnail_data:
        print(f"\t\t - Thumbnail Data...")
        infos_variables['DESCRIPTION'] = handle_text.sanitize(description)
        
        channel = database.title_channel(video_data['title_id'])
        infos_variables['ALLOWED_EXPRESSIONS'] = assets.get_allowed_expressions(channel['id'])
        prompt = database.get_prompt_template('build', 'thumbnail_data', infos_variables)   
        thumbnail_data_text = gemini.run(prompt_json=prompt)
        thumbnail_data = handle_text.format_json_response(thumbnail_data_text)
        database.update('videos', video_data['id'], 'thumbnail_data', thumbnail_data)

    thumbnail_prompt = video_data['thumbnail_prompt']
    if not thumbnail_prompt:
        print(f"\t\t - Thumbnail prompt...")
        infos_variables['THUMBNAIL_PHRASE'] = handle_text.sanitize(thumbnail_data['phrase'])
        infos_variables['THUMBNAIL_EXPRESSION'] = handle_text.sanitize(thumbnail_data['expression'])
        prompt = database.get_prompt_template('build', 'thumbnail', infos_variables)   
        thumbnail_prompt = gemini.run(prompt_json=prompt)
        database.update('videos', video_data['id'], 'thumbnail_prompt', thumbnail_prompt)

def run(video_data, variables):
    infos_variables = {
        "VIDEO_TITLE": handle_text.sanitize(variables['VIDEO_TITLE']),
        "RATIONALE": handle_text.sanitize(variables['RATIONALE']),
        "FULL_SCRIPT": handle_text.sanitize(variables['FULL_SCRIPT']),
        "LANGUAGE": handle_text.sanitize(variables['LANGUAGE_AND_REGION']),
        "TOPICS": handle_text.sanitize(str(variables['TOPICS']))
    }

    description = handle_description(video_data, infos_variables)
    generate_thumbnail_prompt(video_data, infos_variables, description)
    
    return