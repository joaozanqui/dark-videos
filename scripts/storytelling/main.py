from scripts.storytelling.variables import get_variables
import scripts.images.main as images
from string import Template
import os
from scripts.utils import get_gemini_model, analyze_with_gemini, export, get_final_language, get_videos_duration
import json

def build_prompt_template(variables, step, agent=False):
    # print(f"\t\t\t - step: {step}...")
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

def handle_variables(channel, channel_n):
    variables_path = "storage/variables/"
    variables_file = f"{variables_path}{channel_n}.json"

    if os.path.exists(variables_file):
        with open(variables_file, "r", encoding="utf-8") as file:
            variables = json.load(file)     
        return variables


    with open('storage/analysis/insights_p1.txt', "r", encoding="utf-8") as file:
        phase1_insights = file.read() 
    with open('storage/analysis/insights_p2.txt', "r", encoding="utf-8") as file:
        phase2_insights = file.read() 
    with open('storage/analysis/insights_p3.txt', "r", encoding="utf-8") as file:
        phase3_insights = file.read()     

    language = get_final_language()
    duration = get_videos_duration()

    variables = get_variables(phase1_insights, phase2_insights, phase3_insights, channel)
    variables['LANGUAGE_AND_REGION'] = language
    variables['VIDEO_DURATION'] = duration
    
    export(channel_n, variables, format='json', path=f"")
    return variables


def run():
    with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
        channels = json.load(file)    

    for i, channel in enumerate(channels):
        print(channel['name'])
        with open(f"storage/ideas/titles/{i}.json", "r", encoding="utf-8") as file:
            titles = json.load(file)

        print(f" - Variables...")
        variables = handle_variables(channel, i)

        for j, title in enumerate(titles):
            video_path = f"storage/thought/{i}/{j}/"

            if os.path.exists(f"{video_path}topics.txt") and os.path.exists(f"{video_path}full_script.txt") and os.path.exists(f"{video_path}image_prompt.txt"):
                continue

            print(f"\t - {title['title']}")
    
            variables['VIDEO_TITLE'] =  title['title']
            variables['RATIONALE'] =  title['rationale']

            print(f"\t\t - Topics...")
            topics = create_agent_and_run_prompt(variables, i, j, prompts=['topics'], agent_name='topics')
            variables['TOPICS'] = topics
    
            print(f"\t\t - Full script...")
            full_script = create_agent_and_run_prompt(variables, i, j, prompts=['script_structure', 'script'], agent_name='script')
            if full_script:
                image_prompt = images.run(variables['VIDEO_TITLE'], variables['RATIONALE'], full_script)
                print(f"\t\t - Image prompt...")
                export("image_prompt", image_prompt, path=video_path)

                image_path = f"images/{i}/{j}/"
                os.makedirs(image_path, exist_ok=True)

                print(f"\t\t - Done!")
    return