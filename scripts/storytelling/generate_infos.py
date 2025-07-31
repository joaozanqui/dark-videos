import os
import scripts.utils.gemini as gemini
import scripts.utils.handle_text as handle_text
import scripts.database as database

def generate_descritpion(channel_id, title_id, video_path, infos_variables):
    has_description = os.path.exists(f"{video_path}description.txt")

    if not has_description:
        print(f"\t\t - Video Description...")
        prompt = database.build_prompt('build', 'video_description', infos_variables, send_as_json=True)   
        description = gemini.run(prompt_json=prompt)
        database.export("description", description, path=video_path)
    else:
        description = database.get_video_description(channel_id, title_id)

def generate_thumbnail_prompt(channel_id, title_id, video_path, infos_variables, description):
    has_thumbnail_data = os.path.exists(f"{video_path}thumbnail_data.json")  
    has_thumbnail_prompt = os.path.exists(f"{video_path}thumbnail_prompt.txt")  

    if not has_thumbnail_data:
        print(f"\t\t - Thumbnail Data...")
        infos_variables['DESCRIPTION'] = handle_text.sanitize(description)
        infos_variables['ALLOWED_EXPRESSIONS'] = database.get_assets_allowed_expressions(channel_id)
        prompt = database.build_prompt('build', 'thumbnail_data', infos_variables, send_as_json=True)   
        thumbnail_data_text = gemini.run(prompt_json=prompt)
        thumbnail_data = handle_text.format_json_response(thumbnail_data_text)                
        database.export("thumbnail_data", thumbnail_data, format='json', path=video_path)
    else:
        thumbnail_data = database.get_thumbnail_data(channel_id, title_id)

    if not has_thumbnail_prompt:
        print(f"\t\t - Thumbnail prompt...")
        infos_variables['THUMBNAIL_PHRASE'] = handle_text.sanitize(thumbnail_data['phrase'])
        infos_variables['THUMBNAIL_EXPRESSION'] = handle_text.sanitize(thumbnail_data['expression'])
        prompt = database.build_prompt('build', 'thumbnail', infos_variables, send_as_json=True)   
        thumbnail_prompt = gemini.run(prompt_json=prompt)
        database.export("thumbnail_prompt", thumbnail_prompt, path=video_path)
    else:
        thumbnail_prompt = database.get_thumbnail_prompt(channel_id, title_id)

def run(channel_id, title_id, video_path, variables):
    infos_variables = {
        "VIDEO_TITLE": handle_text.sanitize(variables['VIDEO_TITLE']),
        "RATIONALE": handle_text.sanitize(variables['RATIONALE']),
        "FULL_SCRIPT": handle_text.sanitize(database.get_full_script(channel_id, title_id)),
        "LANGUAGE": handle_text.sanitize(variables['LANGUAGE_AND_REGION']),
        "TOPICS": handle_text.sanitize(str(variables['TOPICS']))
    }

    description = generate_descritpion(channel_id, title_id, video_path, infos_variables)
    generate_thumbnail_prompt(channel_id, title_id, video_path, infos_variables, description)
