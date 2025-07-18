from scripts.utils import get_prompt, export, analyze_with_gemini, get_final_language
import re
import os
import json

def channel_instructions(channel):
    text = f"**Channel Name:** {channel['name']}\n**Niche:** {channel['type']}\n**Target Audience:** {channel['public']}\n**Channel's Main Objective:** {channel['main_concept']}\n**Language Style:** {channel['style']}\n**Channel Overview:** {channel['explanation']}"

    return text

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
        "phase1_insights": phase1_insights,
        "phase2_insights": phase2_insights,
        "phase3_insights": phase3_insights,
        "channel": channel_instructions(channel),
        "json_format_response": json_format_response,
        "language": language
    }

    variables.update(other_variables)
    
    template_prompt_file = "default_prompts/script/titles-generation.txt"
    prompt = get_prompt(template_prompt_file, variables)

    export_path = f"storage/prompts/{channel['id']}/"
    export('titles', prompt, path=export_path)

    return prompt

def run(channel_id):
    prompt_file = f"storage/prompts/{channel_id}/titles.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as file:
            prompt = file.read() 
    else:
        return []
    
    title_ideas = analyze_with_gemini(prompt)
    
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
