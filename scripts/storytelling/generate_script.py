import re
import unicodedata
import langid
import scripts.database as database
import scripts.utils.handle_text as handle_text

def is_language_right(text, language):
    language_code = handle_text.get_language_code(language)
    lang, _ = langid.classify(text)
    if lang != language_code:
        print(f"\t\t -Wrong language ({lang}), it must be {language}")

    return lang == language_code

def normalize(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8").lower()
    text = re.sub(r'[^\w\s]', '', text) 
    return text

def has_multiple_forbidden_terms(full_script, language):
    normalized = normalize(full_script)
    pattern = r'\*\*|\b(?:sub[-_\s]?)?(tema|topico|\(topic|topic\)|Topic|theme|visual)\b'
    matches = re.findall(pattern, normalized)

    error = len(matches) > 1 or not is_language_right(full_script, language)

    if error:
        database.export('full_script', full_script, path='./')
        print("\t\t\t - Script generated with forbidden terms... Trying again...")

    return error

def save_topics_variables(topics, video_duration):
    introduction = topics['introduction'][0]
    developments = topics['development']
    conclusion = topics['conclusion'][0]
    total_topics_qty = 3
    introduction_and_conclusion_duration = video_duration / total_topics_qty
    development_duration = video_duration * (2 / total_topics_qty)

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

def run(variables, agent, channel_n, title_n, video_title, script_template_prompt, attempt=0):
    topics_variables = save_topics_variables(variables['TOPICS'], variables['VIDEO_DURATION'])
    variables.update(topics_variables)
    
    chat_history = agent.start_chat(history=[])
    script_structure_prompt = script_template_prompt.safe_substitute(variables)
    chat = chat_history.send_message(script_structure_prompt)
    introduction_prompt = database.build_prompt('script', 'script_introduction', variables, send_as_json=True)   
    chat = chat_history.send_message(introduction_prompt)
    introducion = chat.text

    full_script = introducion
    if has_multiple_forbidden_terms(introducion, variables['LANGUAGE_AND_REGION']) and attempt <= 5:
        attempt += 1
        return run(variables, agent, channel_n, title_n, video_title, script_template_prompt, attempt)
    
    for i, development_topic in enumerate(variables['DEVELOPMENTS']):
        variables['DEVELOPMENT_CHAPTER_NUMBER'] = i + 1
        variables['DEVELOPMENT_TITLE'] = handle_text.sanitize(development_topic['title'])
        variables['DEVELOPMENT_SUBTOPIC_1'] = handle_text.sanitize(development_topic['subtopic_1'])
        variables['DEVELOPMENT_SUBTOPIC_2'] = handle_text.sanitize(development_topic['subtopic_2'])
        variables['DEVELOPMENT_SUBTOPIC_3'] = handle_text.sanitize(development_topic['subtopic_3'])
        variables['DEVELOPMENT_SUBTOPIC_4'] = handle_text.sanitize(development_topic['subtopic_4'])
        variables['DEVELOPMENT_SUBTOPIC_5'] = handle_text.sanitize(development_topic['subtopic_5'])

        prompt = database.build_prompt('script', 'script_go_next_development', variables, send_as_json=True)   
        chat = chat_history.send_message(prompt)
        full_script += chat.text

        if has_multiple_forbidden_terms(chat.text, variables['LANGUAGE_AND_REGION']) and attempt <= 5:
            attempt += 1
            return run(variables, agent, channel_n, title_n, video_title, script_template_prompt, attempt)
    
    prompt = database.build_prompt('script', 'script_conclusion', variables, send_as_json=True)   
    chat = chat_history.send_message(prompt)
    full_script += chat.text

    if has_multiple_forbidden_terms(chat.text, variables['LANGUAGE_AND_REGION']) and attempt <= 5:
        attempt += 1
        return (variables, agent, channel_n, title_n, video_title, script_template_prompt, attempt)

    database.export(f"full_script", full_script, path=f"storage/thought/{channel_n}/{title_n}/")        
    return full_script