from scripts.utils import get_prompt, export, analyze_with_gemini, get_final_language
import re
import json

def channel_instructions(channel):
    text = f"**Channel Name:** {channel['name']}\n**Niche:** {channel['type']}\n**Target Audience:** {channel['public']}\n**Channel's Main Objective:** {channel['main_concept']}\n**Language Style:** {channel['style']}\n**Channel Overview:** {channel['explanation']}"

    return text

def titles_generation_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    channel: str,
    language: str
) -> str:
    json_format_response = f'''[{{"title": "title in {language}", "rationale": "explanation text"}}]'''

    variables = {
        "phase1_insights": phase1_insights,
        "phase2_insights": phase2_insights,
        "phase3_insights": phase3_insights,
        "channel": channel_instructions(channel),
        "json_format_response": json_format_response,
        "language": language
    }
    
    prompt_file = "scripts/ideas/prompts/titles-generation.txt"
    return get_prompt(prompt_file, variables)

def run(insights_p1, insights_p2, insights_p3, channel, model):
    language = get_final_language()

    prompt = titles_generation_prompt(insights_p1, insights_p2, insights_p3, channel, language)   
    title_ideas = analyze_with_gemini(prompt, model)
    
    if not title_ideas:
        print("Failed to generate title ideas from Phase 4.")
        return None
    
    try:
        titles_clean = re.sub(r'^```json\n|```$', '', title_ideas.strip())
        titles_json = json.loads(titles_clean)
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        return None

    print("\nGenerated Viral Video Title Ideas (for your new agent/scripts):")
    
    return titles_json
