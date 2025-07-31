import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.utils.gemini as gemini
import re
import json

def build_title_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    channel: dict,
) -> str:
    language = database.get_input_final_language()
    json_format_response = f'''[{{"title": "title in {language}", "rationale": "explanation text"}}]'''
    variables = database.get_variables(channel['id'])

    other_variables = {
        "phase1_insights": handle_text.sanitize(phase1_insights),
        "phase2_insights": handle_text.sanitize(phase2_insights),
        "phase3_insights": handle_text.sanitize(phase3_insights),
        "channel": handle_text.sanitize(str(channel)),
        "json_format_response": handle_text.sanitize(json_format_response),
        "language": language
    }

    variables.update(other_variables)
    
    prompt = database.build_prompt('script', 'titles-generation', variables)
    prompt_json = json.loads(prompt)

    export_path = f"storage/prompts/{channel['id']}/"
    database.export('titles', prompt_json, format='json',path=export_path)

    return prompt

def run(channel_id):
    file_name = 'titles'
    prompt = database.get_prompt_file(channel_id, file=file_name)
    title_ideas = gemini.run(prompt_json=prompt)
    
    if not title_ideas:
        print("Failed to generate title ideas from Phase 4.")
        return None
    
    try:
        titles_clean = re.sub(r'^```json\n|```$', '', title_ideas.strip())
        titles_json = json.loads(titles_clean)
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        return run(channel_id)

    print("\nGenerated Viral Video Title Ideas (for your new agent/scripts):")

    title_ideas_path = database.export(f"{channel_id}", titles_json, format='json',path='storage/ideas/titles/')
    print(f"Title Ideas saved at {title_ideas_path}")
    
    return titles_json
