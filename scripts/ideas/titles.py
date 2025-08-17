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

def run(channel_id):
    prompt = database.get_prompt_file(channel_id, 'titles')
    title_ideas = gemini.run(prompt_json=prompt)
    titles_json = handle_text.format_json_response(title_ideas)
    if not titles_json:
        return run(channel_id)

    print("\nGenerated Viral Video Title Ideas (for your new agent/scripts):")
    for i, title in enumerate(titles_json):
        print(f"({i}) / {title['title']} - {title['rationale']}\n")

    confirm = inputs.yes_or_no("Confirm the titles?")

    if not confirm:
        return run(channel_id)
    
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
    
    return titles_json
