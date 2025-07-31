from scripts.utils import get_prompt, analyze_with_gemini
import scripts.sanitize as sanitize
import scripts.database as database
import re
import json

def build_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    channel: dict,
) -> str:
    language = database.get_input_final_language()
    json_format_response = f'''[{{"title": "title in {language}", "rationale": "explanation text"}}]'''
    variables = database.get_variables(channel['id'])

    other_variables = {
        "phase1_insights": sanitize.text(phase1_insights),
        "phase2_insights": sanitize.text(phase2_insights),
        "phase3_insights": sanitize.text(phase3_insights),
        "channel": sanitize.text(str(channel)),
        "json_format_response": sanitize.text(json_format_response),
        "language": language
    }

    variables.update(other_variables)
    
    template_prompt_file = "default_prompts/script/titles-generation.json"
    prompt = get_prompt(template_prompt_file, variables)
    prompt_json = json.loads(prompt)

    export_path = f"storage/prompts/{channel['id']}/"
    database.export('titles', prompt_json, format='json',path=export_path)

    return prompt

def run(channel_id):
    file_name = 'titles'
    prompt = database.get_prompt_file(channel_id, file=file_name)
    title_ideas = analyze_with_gemini(prompt_json=prompt)
    
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
