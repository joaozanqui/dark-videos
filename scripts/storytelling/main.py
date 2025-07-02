from scripts.storytelling.variables import get_variables
import os
from scripts.utils import get_gemini_model, analyze_with_gemini, export, get_final_language, get_videos_duration, format_json_response
import json
import scripts.storytelling.generate_script as generate_script 
from scripts.storytelling.utils import build_prompt_template

def get_topics(step_name, variables, agent):
    try:
        prompt = build_prompt_template(variables, step=step_name)   
        response = analyze_with_gemini(prompt, gemini_model=agent)  
        topics = format_json_response(response)  

        return topics
    except Exception as e:
        print(f"\t\t-Error to get topics: Invalid Format")
        return []


def create_agent_and_run_prompt(variables, channel_n, title_n, prompts, agent_name, video_title):
    agent_instructions = build_prompt_template(variables, step=agent_name, agent=True)
    agent = get_gemini_model(agent_instructions=agent_instructions)
    
    has_chat_history = len(prompts) > 1
    if has_chat_history:
        return generate_script.run(variables, prompts, agent, channel_n, title_n, video_title)
    
    step_name = prompts[0]    
    topics = []
    
    while not len(topics):
        topics = get_topics(step_name, variables, agent)

    export(step_name, topics, format='json', path=f"storage/thought/{channel_n}/{title_n}/")

    return topics

def handle_variables(channel, channel_n, language):
    variables_file = f"storage/thought/{channel_n}/variables.json"

    if os.path.exists(variables_file):
        with open(variables_file, "r", encoding="utf-8") as file:
            variables = json.load(file)     
        return variables
    
    print(f" - Variables...")

    with open('storage/analysis/insights_p1.txt', "r", encoding="utf-8") as file:
        phase1_insights = file.read() 
    with open('storage/analysis/insights_p2.txt', "r", encoding="utf-8") as file:
        phase2_insights = file.read() 
    with open('storage/analysis/insights_p3.txt', "r", encoding="utf-8") as file:
        phase3_insights = file.read()     

    duration = get_videos_duration()

    variables = get_variables(phase1_insights, phase2_insights, phase3_insights, channel)

    def has_invalid_keys():
        invalid_keys = []

        for key in variables:
            if "," in key:
                invalid_keys.append(key)

        return len(invalid_keys) > 0
    
    if not variables or has_invalid_keys():
        return handle_variables(channel, channel_n, language)

    variables['LANGUAGE_AND_REGION'] = language
    variables['VIDEO_DURATION'] = duration
    
    export('variables', variables, format='json', path=f"storage/thought/{channel_n}/")
    return variables


def run():
    language = get_final_language()

    with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
        channels = json.load(file)    

    for i, channel in enumerate(channels):
        print(f"- {channel['name']}")
        with open(f"storage/ideas/titles/{i}.json", "r", encoding="utf-8") as file:
            titles = json.load(file)

        variables = handle_variables(channel, i, language)

        for j, title in enumerate(titles):
            video_path = f"storage/thought/{i}/{j}/"
            
            has_topics = os.path.exists(f"{video_path}topics.json") or os.path.exists(f"{video_path}topics.txt")
            has_full_script = os.path.exists(f"{video_path}full_script.txt")
            has_image_prompt = os.path.exists(f"{video_path}image_prompt.txt")
            has_description = os.path.exists(f"{video_path}description.txt")
            has_all_files = has_topics and  has_full_script and has_image_prompt and has_description
            
            if has_all_files:
                continue

            print(f"\t-({i}/{j}) {title['title']}")
            variables['VIDEO_TITLE'] =  title['title']
            variables['RATIONALE'] =  title['rationale']

            if not has_topics:
                print(f"\t\t - Topics...")
                topics = create_agent_and_run_prompt(variables, i, j, prompts=['topics'], agent_name='topics', video_title=title['title'])
                variables['TOPICS'] = topics
            else:
                with open(f"{video_path}topics.json", "r", encoding="utf-8") as file:
                    variables['TOPICS'] = json.load(file) 
    
            if not has_full_script:
                print(f"\t\t - Full script...")
                full_script = create_agent_and_run_prompt(variables, i, j, prompts=['script_structure', 'script_introduction'], agent_name='script', video_title=title['title'])
            else:
                with open(f"{video_path}full_script.txt", "r", encoding="utf-8") as file:
                    full_script = file.read()

            if full_script:
                infos_variables = {
                    "VIDEO_TITLE": variables['VIDEO_TITLE'],
                    "RATIONALE": variables['RATIONALE'],
                    "FULL_SCRIPT": full_script,
                    "LANGUAGE": variables['LANGUAGE_AND_REGION']
                }

                if not has_image_prompt:
                    print(f"\t\t - Image prompt...")
                    prompt = build_prompt_template(infos_variables, step="image")
                    image_prompt = analyze_with_gemini(prompt)
                    export("image_prompt", image_prompt, path=video_path)
                else:
                    with open(f"{video_path}image_prompt.txt", "r", encoding="utf-8") as file:
                        image_prompt = file.read()  

                if not has_description:
                    print(f"\t\t - Description...")
                    prompt = build_prompt_template(infos_variables, step="description")
                    description = analyze_with_gemini(prompt)
                    export("description", description, path=video_path)
                else:
                    with open(f"{video_path}description.txt", "r", encoding="utf-8") as file:
                        description = file.read()  

                print(f"\t\t - Done!")
    return