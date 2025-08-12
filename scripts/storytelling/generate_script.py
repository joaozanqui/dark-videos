import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini

def save_topics_variables(topics: dict, video_duration: int, number_of_dev_topics: int):
    introduction = topics['introduction'][0]
    developments = topics['development']
    conclusion = topics['conclusion'][0]
    total_topics_qty = 3
    introduction_and_conclusion_duration = video_duration / (total_topics_qty*2)
    development_duration = (video_duration * 2) / (total_topics_qty * number_of_dev_topics)

    introduction_bullet_points = [
        introduction[key]
        for key in sorted(introduction.keys())
        if key.startswith("bullet_point")
    ]

    conclusion_bullet_points = [
        conclusion[key]
        for key in sorted(conclusion.keys())
        if key.startswith("bullet_point")
    ]

    variables = {
        "INTRODUCTION_TITLE": introduction['title'],
        "INTRODUCTION_BULLET_POINTS": "; ".join(f"{handle_text.sanitize(point)}" for point in introduction_bullet_points),
        "DEVELOPMENTS": developments,
        "DEVELOPMENT_QTY": len(developments),
        "CONCLUSION_TITLE": conclusion['title'],
        "CONCLUSION_BULLET_POINTS": "; ".join(f"- {handle_text.sanitize(point)}" for point in conclusion_bullet_points),
        "INTRODUCTION_DURATION": introduction_and_conclusion_duration / 2,
        "DEVELOPMENT_DURATION": development_duration,
        "CONCLUSION_DURATION": introduction_and_conclusion_duration / 2
    }

    return variables

def validate(script, language, attempts, duration):
    if attempts > 5:
        return True
    
    if (len(script) > duration * 1500) or (len(script) < duration * 500):
        database.log('full_script', script)
        print(len(script))
        print(duration)
        print(duration * 1500)
        print(f"\t\t\t- Wrong script duration (trying again)...")
        return False
    
    is_text_correct = not handle_text.is_text_wrong(script, language)
    
    if not is_text_correct:
        database.log('full_script', script)

    return is_text_correct

def initialize_chat(script_agent_prompt: str, script_template_prompt: dict, variables: dict):
    chat = gemini.new_chat(script_agent_prompt)
    script_structure_prompt = handle_text.substitute_variables_in_json(script_template_prompt, variables)

    try:
        chat.send_message(str(script_structure_prompt))
    except Exception as e:
        print(f"Error initializing gemini chat: {e}")
        gemini.goto_next_model()
        return initialize_chat(script_agent_prompt, script_template_prompt, variables)

    return chat

def introduction_chat(chat, variables, attempts=0):
    introduction_prompt = database.get_prompt_template('script', 'script_introduction', variables)   
    last_response = chat.send_message(str(introduction_prompt))
    script = last_response.text

    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['INTRODUCTION_DURATION']):
        attempts += 1
        return introduction_chat(chat, variables, attempts)
    
    return script

def chapter_chat(chat, chapter, development_topics, variables, attempts=0):
    variables['DEVELOPMENT_CHAPTER_NUMBER'] = chapter + 1
    variables['DEVELOPMENT_TITLE'] = handle_text.sanitize(development_topics['title'])
    variables['DEVELOPMENT_SUBTOPIC_1'] = handle_text.sanitize(development_topics['subtopic_1'])
    variables['DEVELOPMENT_SUBTOPIC_2'] = handle_text.sanitize(development_topics['subtopic_2'])
    variables['DEVELOPMENT_SUBTOPIC_3'] = handle_text.sanitize(development_topics['subtopic_3'])
    variables['DEVELOPMENT_SUBTOPIC_4'] = handle_text.sanitize(development_topics['subtopic_4'])
    variables['DEVELOPMENT_SUBTOPIC_5'] = handle_text.sanitize(development_topics['subtopic_5'])

    prompt = database.get_prompt_template('script', 'script_go_next_development', variables)   
    last_response = chat.send_message(str(prompt))
    script = last_response.text
    
    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['DEVELOPMENT_DURATION']):
        attempts += 1
        return chapter_chat(chat, chapter, development_topics, variables)
    
    return script

def development_chat(chat, variables, attempts=0):
    script = ''
    for chapter, development_topics in enumerate(variables['DEVELOPMENTS']):
        print(f"\t\t\t- Chapter {chapter+1}...")
        chapter_script = chapter_chat(chat, chapter, development_topics, variables)        
        script += chapter_script
    
    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, (variables['DEVELOPMENT_DURATION']*variables['NUMBER_OF_DEV_TOPICS'])):
        attempts += 1
        return development_chat(chat, variables, attempts)
    
    return script

def conclusion_chat(chat, variables, attempts=0):
    prompt = database.get_prompt_template('script', 'script_conclusion', variables)   
    last_response = chat.send_message(str(prompt))

    script = last_response.text


    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['CONCLUSION_DURATION']):
        attempts += 1
        return conclusion_chat(chat, variables, attempts)

    return script

def chat_with_model(script_agent_prompt: str, script_template_prompt: dict, variables: dict, attempts=0):
    chat = initialize_chat(script_agent_prompt, script_template_prompt, variables)
    
    print(f"\t\t\t- Introduction...")
    introduction_script = introduction_chat(chat, variables)
    print(f"\t\t\t- Development...")
    development_script = development_chat(chat, variables)
    print(f"\t\t\t- Conclusion...")
    conclusion_script = conclusion_chat(chat, variables)
    
    full_script = introduction_script + "\n" + development_script + "\n" + conclusion_script

    return full_script


def run(variables: dict, script_agent_prompt: str, script_template_prompt: dict):
    topics_variables = save_topics_variables(variables['TOPICS'], variables['VIDEO_DURATION'], variables['NUMBER_OF_DEV_TOPICS'])
    variables.update(topics_variables)
    
    full_script = chat_with_model(script_agent_prompt, script_template_prompt, variables)

    return full_script