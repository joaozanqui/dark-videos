from scripts.utils import get_prompt, export, analyze_with_gemini, get_final_language, sanitize_text
import re
import os
import json

def build_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    channel: dict,
    variables: dict
) -> str:
    language = get_final_language()
    json_format_response = f'''[{{"title": "title in {language}", "rationale": "explanation text"}}]'''

    other_variables = {
        "phase1_insights": sanitize_text(phase1_insights),
        "phase2_insights": sanitize_text(phase2_insights),
        "phase3_insights": sanitize_text(phase3_insights),
        "channel": sanitize_text(str(channel)),
        "json_format_response": sanitize_text(json_format_response),
        "language": language
    }

    variables.update(other_variables)
    
    template_prompt_file = "default_prompts/script/titles-generation.json"
    prompt = get_prompt(template_prompt_file, variables)
    prompt_json = json.loads(prompt)

    export_path = f"storage/prompts/{channel['id']}/"
    export('titles', prompt_json, format='json',path=export_path)

    return prompt

def run(channel_id):
    prompt_file = f"storage/prompts/{channel_id}/titles.json"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as file:
            prompt = file.read() 
    else:
        return []
    
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

    title_ideas_path = export(f"{channel_id}", titles_json, format='json',path='storage/ideas/titles/')
    print(f"Title Ideas saved at {title_ideas_path}")
    
    return titles_json
