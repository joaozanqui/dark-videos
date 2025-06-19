from storytelling.variables import get_variables
from string import Template
from scripts.utils import get_gemini_model, analyze_with_gemini, export

def build_prompt_template(variables, step, agent=False):
    template_path = f"storytelling/{'agents' if agent else 'prompts'}/{step}.txt"
    with open(template_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    template = Template(prompt_template)
    
    prompt = template.safe_substitute(variables)
    return prompt

def generate_script(variables, prompts, agent):
    chat_history = agent.start_chat(history=[])
    
    topics_qty = variables['NUMBER_OF_INTRO_TOPICS'] + variables['NUMBER_OF_DEV_TOPICS'] + variables['NUMBER_OF_CONCLUSION_TOPICS']
    
    for step_name in prompts:
        prompt = build_prompt_template(variables, step=step_name)   
        chat = chat_history.send_message(prompt)
        response = chat.text
        export(step_name, response, path='storage/scripts/steps/')
        
    full_script = ''
    
    for i in range(topics_qty - 1):
        step_name = 'script_go_next'
        prompt = build_prompt_template(variables, step=step_name)   
        chat = chat_history.send_message(prompt)
        response = chat.text
        full_script += response
        
        step_name = f"script_{i+2}"
        export(f"{step_name}", response, path='storage/scripts/steps/')        
    
    export(f"full_script", full_script, path='storage/scripts/')        
    return full_script

def run_process(variables, prompts, agent_name):
    agent_instructions = build_prompt_template(variables, step=agent_name, agent=True)
    agent = get_gemini_model(agent_instructions=agent_instructions)
    
    has_chat_history = len(prompts) > 1
    if has_chat_history:
        return generate_script(variables, prompts, agent)
    
    step_name = prompts[0]
    prompt = build_prompt_template(variables, step=step_name)   
    response = analyze_with_gemini(prompt, gemini_model=agent)    
    export(step_name, response)

    return response


def run(phase1_insights=None, phase2_insights=None, phase3_insights=None):
    if not phase1_insights:
        with open('storage/analysis/insights_p1.txt', "r", encoding="utf-8") as file:
            phase1_insights = file.read() 
    if not phase2_insights:
        with open('storage/analysis/insights_p2.txt', "r", encoding="utf-8") as file:
            phase2_insights = file.read() 
    if not phase3_insights:
        with open('storage/analysis/insights_p3.txt', "r", encoding="utf-8") as file:
            phase3_insights = file.read()         
    variables = get_variables(phase1_insights, phase2_insights, phase3_insights)
    
    # pegar os titulos / lingua selecionada / tempo do video
    variables['VIDEO_TITLE'] = "7 Passos para Libertar-se de Feridas Emocionais 💔"
    variables['LANGUAGE_AND_REGION'] = 'Portuguese (BR)'
    variables['VIDEO_DURATION'] = '25min'
    export('variables', variables, format='json')
    
    topics = run_process(variables, prompts=['topics'], agent_name='topics')
    variables['TOPICS'] = topics
    
    # tirar os exports, só deixar o ultimo e o script_structure
    script = run_process(variables, prompts=['script_structure', 'script'], agent_name='script')
    
    return