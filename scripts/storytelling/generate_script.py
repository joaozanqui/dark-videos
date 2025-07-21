import re
import unicodedata
import langid
from scripts.storytelling.utils import build_template
from scripts.utils import get_language_code, export

def is_language_right(text, language):
    language_code = get_language_code(language)
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
    pattern = r'\*\*|\b(?:sub[-_\s]?)?(tema|topico|topic|theme)\b'
    matches = re.findall(pattern, normalized)

    error = len(matches) > 1 or not is_language_right(full_script, language)

    if error:
        print("\t\t -Script generated with forbidden terms... Trying again...")

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
        "INTRODUCTION_BULLET_POINTS": "; ".join(f"{point}" for point in introduction_bullet_points),
        "DEVELOPMENTS": developments,
        "DEVELOPMENT_QTY": len(developments),
        "CONCLUSION_TITLE": conclusion['title'],
        "CONCLUSION_BULLET_POINTS": "; ".join(f"- {point}" for point in conclusion_bullet_points),
        "INTRODUCTION_DURATION": introduction_and_conclusion_duration / 2,
        "DEVELOPMENT_DURATION": development_duration,
        "CONCLUSION_DURATION": introduction_and_conclusion_duration / 2
    }

    return variables

def run(variables, agent, channel_n, title_n, video_title, script_template_prompt):
    topics_variables = save_topics_variables(variables['TOPICS'], variables['VIDEO_DURATION'])
    variables.update(topics_variables)
    
    chat_history = agent.start_chat(history=[])
    script_structure_prompt = script_template_prompt.safe_substitute(variables)
    chat = chat_history.send_message(script_structure_prompt)
    introduction_prompt = build_template(variables, step='script', file_name='script_introduction')   
    chat = chat_history.send_message(introduction_prompt)
    introducion = chat.text

    full_script = introducion
    if has_multiple_forbidden_terms(full_script, variables['LANGUAGE_AND_REGION']):
        return run(variables, agent, channel_n, title_n, video_title, script_template_prompt)
    
    for i, development_topic in enumerate(variables['DEVELOPMENTS']):
        variables['DEVELOPMENT_CHAPTER_NUMBER'] = i + 1
        variables['DEVELOPMENT_TITLE'] = development_topic['title']
        variables['DEVELOPMENT_SUBTOPIC_1'] = development_topic['subtopic_1']
        variables['DEVELOPMENT_SUBTOPIC_2'] = development_topic['subtopic_2']
        variables['DEVELOPMENT_SUBTOPIC_3'] = development_topic['subtopic_3']
        variables['DEVELOPMENT_SUBTOPIC_4'] = development_topic['subtopic_4']
        variables['DEVELOPMENT_SUBTOPIC_5'] = development_topic['subtopic_5']

        prompt = build_template(variables, step='script', file_name='script_go_next_development')
        chat = chat_history.send_message(prompt)
        full_script += chat.text

        if has_multiple_forbidden_terms(full_script, variables['LANGUAGE_AND_REGION']):
            return run(variables, agent, channel_n, title_n, video_title, script_template_prompt)
    
    prompt = build_template(variables, step='script', file_name='script_conclusion')
    chat = chat_history.send_message(prompt)
    full_script += chat.text

    if has_multiple_forbidden_terms(full_script, variables['LANGUAGE_AND_REGION']):
        return (variables, agent, channel_n, title_n, video_title, script_template_prompt)

    export(f"full_script", full_script, path=f"storage/thought/{channel_n}/{title_n}/")        
    return full_script