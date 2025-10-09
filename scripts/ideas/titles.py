import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini
import scripts.utils.inputs as inputs
import re
import json

def build_title_prompt(channel: dict, analysis: dict) -> str:
    language = database.get_item('languages', channel['language_id'])
    json_format_response = f'''[{{"title": "title in {language['name']}", "rationale": "explanation text"}}]'''
    variables = database.channel_variables(channel['id'])
    titles = database.channel_titles(channel['id'])

    other_variables = {
        "phase1_insights": handle_text.sanitize(analysis['insights_p1']),
        "phase2_insights": handle_text.sanitize(analysis['insights_p2']),
        "phase3_insights": handle_text.sanitize(analysis['insights_p3']),
        "channel": handle_text.sanitize(str(channel)),
        "json_format_response": handle_text.sanitize(json_format_response),
        "language": language['name'],
        "existing_titles": [title['title'] for title in titles]
    }

    variables.update(other_variables)
    
    prompt_template = database.get_prompt_template('script', 'titles-generation', variables)
    prompt_json = json.loads(prompt_template)
    prompt = database.get_item('prompts', channel['id'], 'channel_id')
    
    if not prompt:
        data = {
            "channel_id": channel['id'],
            "titles": prompt_json
        }
        database.insert(data, 'prompts')
    else:
        database.update('prompts', prompt['id'], 'titles', prompt_json)
    
    return prompt_template

def confirm_saves(titles_json, channel_id):
    print("\nGenerated Viral Video Title Ideas (for your new agent/scripts):")
    for i, title in enumerate(titles_json):
        if not isinstance(title, dict):
            return False
        print(f"({i}) / {title['title']} - {title['rationale']}\n")

    confirm = inputs.yes_or_no("Confirm the titles?")

    if not confirm:
        return False
    
    title_number = database.next_title_number(channel_id)
    for title in titles_json:
        data = {
            "title": title['title'],
            "rationale": title['rationale'],
            "channel_id": channel_id,
            "title_number": title_number
        }
        database.insert(data, 'titles')
        title_number += 1
    
    print(f"Title Ideas saved!")
    return True

def build_copy_prompt(original_titles, channel):
    language = database.get_item('languages', channel['language_id'])['name']
    
    prompt = f"Translate all the {len(original_titles)} following video titles to {language}, maintaining their meaning and impact. Here are the titles:\n\n"
    for i, title in enumerate(original_titles):
        prompt += f"({i+1}) {title}\n"
    prompt += "\nProvide the translated titles as a JSON array format as follows: [{title: \"translated title 1\", rationale: \"Title 1 main rationale explanation\"}, {title: \"translated title 2\", rationale: \"Title 2 main rationale explanation\"}]"

    return prompt

def copy_titles(base_channel_data, titles_qty, channel):
    videos = base_channel_data[2]
    if titles_qty != -1:
        videos = videos[:titles_qty]

    original_titles = [video['title'] for video in videos]
    prompt = build_copy_prompt(original_titles, channel)

    translated_titles = gemini.run(prompt_text=prompt)
    titles_json = handle_text.format_json_response(translated_titles)
    
    if not titles_json or not isinstance(titles_json, list) or len(titles_json) != len(original_titles):
        print("Error in translation or mismatch in number of titles. Retrying...")
        return copy_titles(base_channel_data, titles_qty, channel)
    
    reversed_titles = list(reversed(titles_json))

    if not confirm_saves(titles_json, channel['id']):
        return copy_titles(base_channel_data, titles_qty, channel)
    
    return reversed_titles


def run(channel_id):
    prompt = database.get_prompt_file(channel_id, 'titles')
    title_ideas = gemini.run(prompt_json=prompt)
    titles_json = handle_text.format_json_response(title_ideas)
    if not titles_json or not isinstance(titles_json, list):
        return run(channel_id)

    if not confirm_saves(titles_json, channel_id):
        return run(channel_id)
    
    return titles_json
