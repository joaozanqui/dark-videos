import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini

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

def initialize_chat(script_agent_prompt, script_template_prompt, variables):
    chat = gemini.new_chat(script_agent_prompt)
    script_structure_prompt = script_template_prompt.safe_substitute(variables)

    try:
        chat.send_message(script_structure_prompt)
    except Exception as e:
        print(f"Error initializing gemini chat: {e}")
        gemini.goto_next_model()
        return initialize_chat(script_agent_prompt, script_template_prompt, variables)

    return chat

def introduction_chat(chat, variables):
    introduction_prompt = database.build_prompt('script', 'script_introduction', variables, send_as_json=True)   
    last_response = chat.send_message(introduction_prompt)
    
    return last_response.text

def development_chat(chat, chapter, development_topics, variables):
    variables['DEVELOPMENT_CHAPTER_NUMBER'] = chapter + 1
    variables['DEVELOPMENT_TITLE'] = handle_text.sanitize(development_topics['title'])
    variables['DEVELOPMENT_SUBTOPIC_1'] = handle_text.sanitize(development_topics['subtopic_1'])
    variables['DEVELOPMENT_SUBTOPIC_2'] = handle_text.sanitize(development_topics['subtopic_2'])
    variables['DEVELOPMENT_SUBTOPIC_3'] = handle_text.sanitize(development_topics['subtopic_3'])
    variables['DEVELOPMENT_SUBTOPIC_4'] = handle_text.sanitize(development_topics['subtopic_4'])
    variables['DEVELOPMENT_SUBTOPIC_5'] = handle_text.sanitize(development_topics['subtopic_5'])

    prompt = database.build_prompt('script', 'script_go_next_development', variables, send_as_json=True)   
    last_response = chat.send_message(prompt)
    return last_response.text

def conclusion_chat(chat, variables):
    prompt = database.build_prompt('script', 'script_conclusion', variables, send_as_json=True)   
    last_response = chat.send_message(prompt)

    return last_response.text

def chat_with_model(script_agent_prompt, script_template_prompt, variables, attempts=0):
    language = variables['LANGUAGE_AND_REGION']
    chat = initialize_chat(script_agent_prompt, script_template_prompt, variables)
    
    print(f"\t\t\t- Introduction...")
    introduction_script = introduction_chat(chat, variables)
    if handle_text.is_text_wrong(introduction_script, language) and attempts <= 5:
        attempts += 1
        return chat_with_model(script_agent_prompt, script_template_prompt, variables, attempts)
    
    development_script = ''
    for chapter, development_topics in enumerate(variables['DEVELOPMENTS']):
        print(f"\t\t\t- Chapter {chapter+1}...")
        chapter_script = development_chat(chat, chapter, development_topics, variables)

        if handle_text.is_text_wrong(chapter_script, language) and attempts <= 5:
            attempts += 1
            return chat_with_model(script_agent_prompt, script_template_prompt, variables, attempts)
        
        development_script += chapter_script
    
    print(f"\t\t\t- Conclusion...")
    conclusion_script = conclusion_chat(chat, variables)
    if handle_text.is_text_wrong(conclusion_script, language) and attempts <= 5:
        attempts += 1
        return chat_with_model(script_agent_prompt, script_template_prompt, variables, attempts)
    
    full_script = introduction_script + "\n" + development_script + "\n" + conclusion_script
    return full_script


def run(variables, script_agent_prompt, channel_n, title_n, script_template_prompt):
    topics_variables = save_topics_variables(variables['TOPICS'], variables['VIDEO_DURATION'])
    variables.update(topics_variables)
    
    full_script = chat_with_model(script_agent_prompt, script_template_prompt, variables)

    database.export(f"full_script", full_script, path=f"storage/thought/{channel_n}/{title_n}/")        
    return full_script