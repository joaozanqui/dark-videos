from scripts.utils import get_gemini_model, analyze_with_gemini, export, format_json_response, get_variables, sanitize_text
from scripts.storytelling.utils import build_template
import scripts.storytelling.generate_script as generate_script 
from string import Template
import json
import os

def get_response(variables, prompt_template, agent):
    prompt_str = prompt_template.safe_substitute(variables)
    prompt = json.loads(prompt_str)
    response = analyze_with_gemini(prompt_json=prompt, gemini_model=agent)  

    return response

def get_topics(variables, topics_template_prompt, topics_agent):
    topics_str = get_response(variables, topics_template_prompt, topics_agent)
    try:
        return format_json_response(topics_str)
    except Exception as e:
        print(f"\t\t-Error to get topics: Invalid Format")
        return get_topics(variables, topics_template_prompt, topics_agent)

def get_prompt(channel_id, step, file):
    path = f"storage/prompts/{channel_id}/{step}/{file}.json"

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            prompt = f.read()     
        return prompt
    
    return ''

def run(channel_id):
    with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
        channels = json.load(file)    

    channel = channels[int(channel_id)-1]
    
    print(f"- {channel['name']}")
    with open(f"storage/ideas/titles/{channel_id}.json", "r", encoding="utf-8") as file:
        titles = json.load(file)

    variables = get_variables(channel_id)
    topics_agent_prompt = get_prompt(channel_id, step='agents',file='topics')
    script_agent_prompt = get_prompt(channel_id, step='agents',file='script')
    topics_prompt = get_prompt(channel_id, step='script',file='topics')
    topics_template_prompt = Template(str(topics_prompt))
    script_prompt = get_prompt(channel_id, step='script',file='script')
    script_template_prompt = Template(str(script_prompt))

    if not variables or not topics_agent_prompt or not script_agent_prompt or not topics_template_prompt or not script_template_prompt:
        return []
    
    topics_agent = get_gemini_model(agent_instructions=topics_agent_prompt)
    script_agent = get_gemini_model(agent_instructions=script_agent_prompt)
    
    for title_id, title in enumerate(titles):
        video_path = f"storage/thought/{channel_id}/{title_id}/"
        
        has_topics = os.path.exists(f"{video_path}topics.json") or os.path.exists(f"{video_path}topics.txt")
        has_full_script = os.path.exists(f"{video_path}full_script.txt")
        has_image_prompt = os.path.exists(f"{video_path}image_prompt.txt")
        has_description = os.path.exists(f"{video_path}description.txt")
        has_all_files = has_topics and  has_full_script and has_image_prompt and has_description
        
        if has_all_files:
            continue

        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        variables['VIDEO_TITLE'] =  title['title']
        variables['RATIONALE'] =  title['rationale']

        if not has_topics:
            print(f"\t\t - Topics...")
            variables['TOPICS'] = get_topics(variables, topics_template_prompt, topics_agent)
        else:
            with open(f"{video_path}topics.json", "r", encoding="utf-8") as file:
                variables['TOPICS'] = json.load(file) 

        if not has_full_script:
            print(f"\t\t - Full script...")
            full_script = generate_script.run(variables, script_agent, channel_id, title_id, title['title'], script_template_prompt)
        else:
            with open(f"{video_path}full_script.txt", "r", encoding="utf-8") as file:
                full_script = file.read()

        if full_script:
            infos_variables = {
                "VIDEO_TITLE": variables['VIDEO_TITLE'],
                "RATIONALE": variables['RATIONALE'],
                "FULL_SCRIPT": sanitize_text(full_script),
                "LANGUAGE": variables['LANGUAGE_AND_REGION']
            }

            if not has_image_prompt:
                print(f"\t\t - Thumbnail prompt...")
                prompt = build_template(infos_variables, step='script',file_name="thumbnail")
                thumbnail_prompt = analyze_with_gemini(prompt_json=prompt)
                export("thumbnail_prompt", thumbnail_prompt, path=video_path)
            else:
                with open(f"{video_path}thumbnail_prompt.txt", "r", encoding="utf-8") as file:
                    thumbnail_prompt = file.read()  

            if not has_description:
                print(f"\t\t - Description...")
                prompt = build_template(infos_variables, step='script',file_name="video_description")
                description = analyze_with_gemini(prompt_json=prompt)
                export("description", description, path=video_path)
            else:
                with open(f"{video_path}description.txt", "r", encoding="utf-8") as file:
                    description = file.read()  

            print(f"\t\t - Done!")
    return