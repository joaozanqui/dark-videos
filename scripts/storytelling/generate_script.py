import re
import unicodedata
import langid
from scripts.storytelling.utils import build_prompt_template
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


def has_multiple_forbidden_terms(full_script, video_title, language):
    normalized = normalize(full_script)
    pattern = r'\*\*|\b(?:sub[-_\s]?)?(tema|topico|topic|theme)\b'
    matches = re.findall(pattern, normalized)

    error = len(matches) > 1 or not is_language_right(full_script, language)

    if error:
        print("\t\t -Script generated with forbidden terms... Trying again...")

    return error

def analyse_topics(topics, video_duration):
    introduction = topics[0]['introduction'][0]
    developments = topics[1]['development']
    conclusion = topics[2]['conclusion'][0]
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
        "INTRODUCTION_BULLET_POINTS": "\n".join(f"- {point}" for point in introduction_bullet_points),
        "DEVELOPMENTS": developments,
        "DEVELOPMENT_QTY": len(developments),
        "CONCLUSION_TITLE": conclusion['title'],
        "CONCLUSION_BULLET_POINTS": "\n".join(f"- {point}" for point in conclusion_bullet_points),
        "INTRODUCTION_DURATION": introduction_and_conclusion_duration / 2,
        "DEVELOPMENT_DURATION": development_duration,
        "CONCLUSION_DURATION": introduction_and_conclusion_duration / 2
    }

    return variables

def run(variables, prompts, agent, channel_n, title_n, video_title):
    chat_history = agent.start_chat(history=[])
    topics_variables = analyse_topics(variables['TOPICS'], variables['VIDEO_DURATION'])
    variables.update(topics_variables)
    
    for step_name in prompts:
        prompt = build_prompt_template(variables, step=step_name)   
        chat = chat_history.send_message(prompt)
        response = chat.text
        
    full_script = response
    if has_multiple_forbidden_terms(full_script, video_title, variables['LANGUAGE_AND_REGION']):
        return run(variables, prompts, agent, channel_n, title_n, video_title)    
    
    for i, development_topic in enumerate(variables['DEVELOPMENTS']):
        variables['DEVELOPMENT_CHAPTER_NUMBER'] = i + 1
        variables['DEVELOPMENT_TITLE'] = development_topic['title']
        variables['DEVELOPMENT_SUBTOPIC_1'] = development_topic['subtopic_1']
        variables['DEVELOPMENT_SUBTOPIC_2'] = development_topic['subtopic_2']
        variables['DEVELOPMENT_SUBTOPIC_3'] = development_topic['subtopic_3']
        variables['DEVELOPMENT_SUBTOPIC_4'] = development_topic['subtopic_4']
        variables['DEVELOPMENT_SUBTOPIC_5'] = development_topic['subtopic_5']

        step_name = 'script_go_next_development'
        prompt = build_prompt_template(variables, step=step_name)   

        chat = chat_history.send_message(prompt)
        response = chat.text
        full_script += response
        if has_multiple_forbidden_terms(full_script, video_title, variables['LANGUAGE_AND_REGION']):
            return run(variables, prompts, agent, channel_n, title_n, video_title)
    
    step_name = 'script_conclusion'
    prompt = build_prompt_template(variables, step=step_name)   

    chat = chat_history.send_message(prompt)
    response = chat.text
    full_script += response

    if has_multiple_forbidden_terms(full_script, video_title, variables['LANGUAGE_AND_REGION']):
        return run(variables, prompts, agent, channel_n, title_n, video_title)

    export(f"full_script", full_script, path=f"storage/thought/{channel_n}/{title_n}/")        
    return full_script