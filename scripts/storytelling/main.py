from scripts.storytelling.variables import get_variables
from string import Template
import os
from scripts.utils import get_gemini_model, analyze_with_gemini, export, get_final_language, get_videos_duration
import json

def build_prompt_template(variables, step, agent=False):
    template_path = f"scripts/storytelling/{'agents' if agent else 'prompts'}/"
    template_file = f"{template_path}{step}.txt"

    with open(template_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    template = Template(prompt_template)
    
    prompt = template.safe_substitute(variables)
    return prompt

def generate_script(variables, prompts, agent, channel_n, title_n):
    chat_history = agent.start_chat(history=[])
    
    topics_qty = variables['NUMBER_OF_INTRO_TOPICS'] + variables['NUMBER_OF_DEV_TOPICS'] + variables['NUMBER_OF_CONCLUSION_TOPICS']
    
    for step_name in prompts:
        prompt = build_prompt_template(variables, step=step_name)   
        chat = chat_history.send_message(prompt)
        response = chat.text
        # export(step_name, response, path='storage/scripts/steps/')
        
    full_script = ''
    
    for i in range(topics_qty - 1):
        step_name = 'script_go_next'
        prompt = build_prompt_template(variables, step=step_name)   
        chat = chat_history.send_message(prompt)
        response = chat.text
        full_script += response
        
        step_name = f"script_{i+2}"
        # export(f"{step_name}", response, path=f"storage/scripts/steps/{channel_n}/{title_n}/")        
    
    export(f"full_script", full_script, path=f"storage/thought/{channel_n}/{title_n}/")        
    return full_script

def create_agent_and_run_prompt(variables, channel_n, title_n, prompts, agent_name):
    agent_instructions = build_prompt_template(variables, step=agent_name, agent=True)
    agent = get_gemini_model(agent_instructions=agent_instructions)
    
    has_chat_history = len(prompts) > 1
    if has_chat_history:
        return generate_script(variables, prompts, agent, channel_n, title_n)
    
    step_name = prompts[0]
    prompt = build_prompt_template(variables, step=step_name)   
    response = analyze_with_gemini(prompt, gemini_model=agent)    
    export(step_name, response, path=f"storage/thought/{channel_n}/{title_n}/")

    return response

def handle_variables(channel, channel_n, language):
    variables_path = "storage/variables/"
    variables_file = f"{variables_path}{channel_n}.json"

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
    if not variables:
        return {}
    
    variables['LANGUAGE_AND_REGION'] = language
    variables['VIDEO_DURATION'] = duration
    
    export(channel_n, variables, format='json', path=f"storage/variables/")
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
        while not variables:
            print("Variables Failed!")
            variables = handle_variables(channel, i, language)


        for j, title in enumerate(titles):
            video_path = f"storage/thought/{i}/{j}/"
            
            has_topics = os.path.exists(f"{video_path}topics.txt")
            has_full_script = os.path.exists(f"{video_path}full_script.txt")
            has_image_prompt = os.path.exists(f"{video_path}image_prompt.txt")
            has_description = os.path.exists(f"{video_path}description.txt")
            has_all_files = has_topics and  has_full_script and has_image_prompt and has_description
            
            if has_all_files:
                continue

            print(f"\t- {title['title']}")
            variables['VIDEO_TITLE'] =  title['title']
            variables['RATIONALE'] =  title['rationale']

            if not has_topics:
                print(f"\t\t - Topics...")
                topics = create_agent_and_run_prompt(variables, i, j, prompts=['topics'], agent_name='topics')
                variables['TOPICS'] = topics
            else:
                with open(f"{video_path}topics.txt", "r", encoding="utf-8") as file:
                    variables['TOPICS'] = file.read() 
    
            if not has_full_script:
                print(f"\t\t - Full script...")
                full_script = create_agent_and_run_prompt(variables, i, j, prompts=['script_structure', 'script'], agent_name='script')
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

                image_path = f"storage/images/{i}/{j}/"
                image_path = f"storage/audios/{i}/{j}/"
                os.makedirs(image_path, exist_ok=True)

                print(f"\t\t - Done!")
    return