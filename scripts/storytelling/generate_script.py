import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini

def save_topics_variables(topics: dict, video_duration: int, number_of_dev_topics: int):
    introduction = topics['introduction'][0]
    developments = topics['development']
    conclusion = topics['conclusion'][0]
    total_topics_qty = 3
    introduction_duration = video_duration / (total_topics_qty*2)
    conclusion_duration = video_duration / (total_topics_qty*2)
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

    words_per_minute = 150
    variables = {
        "INTRODUCTION_TITLE": introduction['title'],
        "INTRODUCTION_BULLET_POINTS": "; ".join(f"{handle_text.sanitize(point)}" for point in introduction_bullet_points),
        "DEVELOPMENTS": developments,
        "DEVELOPMENT_QTY": len(developments),
        "CONCLUSION_TITLE": conclusion['title'],
        "CONCLUSION_BULLET_POINTS": "; ".join(f"- {handle_text.sanitize(point)}" for point in conclusion_bullet_points),
        "INTRODUCTION_DURATION": f"{introduction_duration:.2f}",
        "INTRODUCTION_WORDS": f"{introduction_duration*words_per_minute:.2f}",
        "DEVELOPMENT_DURATION": f"{development_duration:.2f}",
        "DEVELOPMENT_WORDS": f"{development_duration*words_per_minute:.2f}",
        "CONCLUSION_DURATION": f"{conclusion_duration:.2f}",
        "CONCLUSION_WORDS": f"{conclusion_duration*words_per_minute:.2f}",
    }

    return variables

def validate(script: str, language: str, attempts: int, duration: str):
    if attempts > 2:
        return True
    
    script_words_qty = len(script.split())
    words_per_minute = 150
    max_words = float(duration) * words_per_minute
    if (script_words_qty > max_words):
        print(f"\t\t\t\t- Wrong script duration (trying again)...")
        return False
    
    if handle_text.is_text_wrong(script, language):
        print(f"\t\t\t\t- Wrong script content (trying again)...")
        gemini.goto_next_model()
        return False

    print("\t\t\t\t- Done!")
    return True

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

def chat_with_model(chat, prompt):
    try:
        last_response = chat.send_message(str(prompt))
    except Exception as e:
        print(f"Error to chat with gemini: {e}")
        gemini.goto_next_model()
        return chat_with_model(chat, prompt)
    script = last_response.text

    return script

def introduction_chat(chat, variables, attempts=0):
    prompt = database.get_prompt_template('script', 'script_introduction', variables)   
    script = chat_with_model(chat, prompt)

    while not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['INTRODUCTION_DURATION']) and attempts < 3:
        attempts += 1
        long_prompt = database.get_prompt_template('script', 'introduction_long_text', variables)   
        script = chat_with_model(chat, long_prompt)
    
    return script

def chapter_chat(chat, chapter, development_topics, variables, attempts=0):
    variables['DEVELOPMENT_CHAPTER_NUMBER'] = chapter + 1
    variables['DEVELOPMENT_TITLE'] = handle_text.sanitize(development_topics['title'])
    variables['DEVELOPMENT_SUBTOPIC_1'] = "Empty"
    variables['DEVELOPMENT_SUBTOPIC_2'] = "Empty"
    variables['DEVELOPMENT_SUBTOPIC_3'] = "Empty"
    variables['DEVELOPMENT_SUBTOPIC_4'] = "Empty"
    variables['DEVELOPMENT_SUBTOPIC_5'] = "Empty"

    if development_topics.get('subtopic_1'):
        variables['DEVELOPMENT_SUBTOPIC_1'] = handle_text.sanitize(development_topics['subtopic_1'])
    if development_topics.get('subtopic_2'):
        variables['DEVELOPMENT_SUBTOPIC_2'] = handle_text.sanitize(development_topics['subtopic_2'])
    if development_topics.get('subtopic_3'):
        variables['DEVELOPMENT_SUBTOPIC_3'] = handle_text.sanitize(development_topics['subtopic_3'])
    if development_topics.get('subtopic_4'):
        variables['DEVELOPMENT_SUBTOPIC_4'] = handle_text.sanitize(development_topics['subtopic_4'])
    if development_topics.get('subtopic_5'):
        variables['DEVELOPMENT_SUBTOPIC_5'] = handle_text.sanitize(development_topics['subtopic_5'])

    prompt = database.get_prompt_template('script', 'script_go_next_development', variables)   
    script = chat_with_model(chat, prompt)

    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['DEVELOPMENT_DURATION']):
        attempts += 1
        long_prompt = database.get_prompt_template('script', 'development_long_text', variables)   
        script = chat_with_model(chat, long_prompt)
    
    return script

def development_chat(chat, variables):
    script = ''
    for chapter, development_topics in enumerate(variables['DEVELOPMENTS']):
        print(f"\t\t\t- Chapter {chapter+1}...")
        chapter_script = chapter_chat(chat, chapter, development_topics, variables)        
        script += chapter_script
    
    return script

def conclusion_chat(chat, variables, attempts=0):
    prompt = database.get_prompt_template('script', 'script_conclusion', variables)   
    script = chat_with_model(chat, prompt)

    if not validate(script, variables['LANGUAGE_AND_REGION'], attempts, variables['CONCLUSION_DURATION']):
        long_prompt = database.get_prompt_template('script', 'conclusion_long_text', variables)   
        script = chat_with_model(chat, long_prompt)

    return script

def handle_process(script_agent_prompt: str, script_template_prompt: dict, variables: dict, attempts=0):
    chat = initialize_chat(script_agent_prompt, script_template_prompt, variables)
    
    print(f"\t\t\t- Introduction...")
    introduction_script = introduction_chat(chat, variables)
    print(f"\t\t\t- Development...")
    development_script = development_chat(chat, variables)
    print(f"\t\t\t- Conclusion...")
    conclusion_script = conclusion_chat(chat, variables)
    
    full_script = introduction_script + "\n" + development_script + "\n" + conclusion_script
    if not validate(full_script, variables['LANGUAGE_AND_REGION'], attempts, variables['VIDEO_DURATION']):
        attempts += 1
        return handle_process(script_agent_prompt, script_template_prompt, variables, attempts)

    return full_script


def run(variables: dict, script_agent_prompt: str, script_template_prompt: dict):
    topics_variables = save_topics_variables(variables['TOPICS'], variables['VIDEO_DURATION'], variables['NUMBER_OF_DEV_TOPICS'])
    variables.update(topics_variables)
    
    full_script = handle_process(script_agent_prompt, script_template_prompt, variables)

    return full_script