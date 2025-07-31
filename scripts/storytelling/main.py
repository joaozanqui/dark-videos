import scripts.database as database
import scripts.utils.gemini as gemini
import scripts.utils.handle_text as handle_text
import scripts.storytelling.generate_script as generate_script
from string import Template
import json
import os

def get_response(variables, prompt_template, agent):
    prompt_str = prompt_template.safe_substitute(variables)
    prompt = json.loads(prompt_str)
    response = gemini.run(prompt_json=prompt, gemini_model=agent)  

    return response

def get_topics(variables, topics_template_prompt, topics_agent):
    topics_str = get_response(variables, topics_template_prompt, topics_agent)
    try:
        return handle_text.format_json_response(topics_str)
    except Exception as e:
        print(f"\t\t-Error to get topics: Invalid Format")
        return get_topics(variables, topics_template_prompt, topics_agent)
    

def set_thumbnail_data(variables, channel_id, title_id):
    video_path = f"storage/thought/{channel_id}/{title_id}/"
    has_description = os.path.exists(f"{video_path}description.txt")
    has_thumbnail_data = os.path.exists(f"{video_path}thumbnail_data.json")  
    has_thumbnail_prompt = os.path.exists(f"{video_path}thumbnail_prompt.txt")  

    infos_variables = {
        "VIDEO_TITLE": handle_text.sanitize(variables['VIDEO_TITLE']),
        "RATIONALE": handle_text.sanitize(variables['RATIONALE']),
        "FULL_SCRIPT": handle_text.sanitize(database.get_full_script(channel_id, title_id)),
        "LANGUAGE": handle_text.sanitize(variables['LANGUAGE_AND_REGION']),
        "TOPICS": handle_text.sanitize(str(variables['TOPICS']))
    }

    if not has_description:
        print(f"\t\t - Video Description...")
        prompt = database.build_prompt('build', 'video_description', infos_variables, send_as_json=True)   
        description = gemini.run(prompt_json=prompt)
        database.export("description", description, path=video_path)
    else:
        description = database.get_video_description(channel_id, title_id)

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

def run(channel_id):
    channel = database.get_channel_by_id(channel_id)

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    variables = database.get_variables(channel_id)
    topics_agent_prompt = database.get_prompt_file(channel_id, step='agents',file='topics')
    script_agent_prompt = database.get_prompt_file(channel_id, step='agents',file='script')
    topics_prompt = database.get_prompt_file(channel_id, step='script',file='topics')
    topics_template_prompt = Template(str(topics_prompt))
    script_prompt = database.get_prompt_file(channel_id, step='script',file='script')
    script_template_prompt = Template(str(script_prompt))

    if not variables or not topics_agent_prompt or not script_agent_prompt or not topics_template_prompt or not script_template_prompt:
        return []
    
    topics_agent = gemini.get_model(agent_instructions=topics_agent_prompt)
    script_agent = gemini.get_model(agent_instructions=script_agent_prompt)
    
    for title_id, title in enumerate(titles):
        video_path = f"storage/thought/{channel_id}/{title_id}"
        
        has_topics = os.path.exists(f"{video_path}/topics.json") or os.path.exists(f"{video_path}/topics.txt")
        has_full_script = os.path.exists(f"{video_path}/full_script.txt")
        has_all_files = has_topics and  has_full_script
        
        if has_all_files:
            continue

        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        variables['VIDEO_TITLE'] =  title['title']
        variables['RATIONALE'] =  title['rationale']

        if not has_topics:
            print(f"\t\t - Topics...")
            variables['TOPICS'] = get_topics(variables, topics_template_prompt, topics_agent)
            if not variables['TOPICS']:
                return run(channel_id)
            database.export('topics', variables['TOPICS'], format='json', path=f"{video_path}/")
            if isinstance(variables['TOPICS'], list):
                variables['TOPICS'] = variables['TOPICS'][0]
        else:
            variables['TOPICS'] = database.get_topics(channel_id, title_id)

        if not has_full_script:
            print(f"\t\t - Full script...")
            full_script = generate_script.run(variables, script_agent, channel_id, title_id, title['title'], script_template_prompt)
        else:
            full_script = database.get_full_script(channel_id, title_id)
        
        if full_script:
            set_thumbnail_data(variables, channel_id, title_id)
    
        print(f"\t\t - Done!")
    return