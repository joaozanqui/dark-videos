from scripts.utils import get_prompt, analyze_with_gemini, export
import json
import re

def new_channel_ideas_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str
) -> str :
    variables = {
        "phase1_insights": phase1_insights,
        "phase2_insights": phase2_insights,
        "phase3_insights": phase3_insights
    }

    prompt_file = "scripts/ideas/prompts/new-channels-ideas.txt"
    return get_prompt(prompt_file, variables)

def run(insights_p1, insights_p2, insights_p3, model):   
    prompt = new_channel_ideas_prompt(insights_p1, insights_p2, insights_p3)   
    ideas = analyze_with_gemini(prompt, model)
    
    if not ideas:
        print("Failed to generate channels ideas")
        return None
    
    try:
        ideas_clean = re.sub(r'^```json\n|```$', '', ideas.strip())
        ideas_json = json.loads(ideas_clean)
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        return None

    print("\nGenerated Viral Channels Ideas (for your new agent/scripts):")
    channels_ideas = export('channels', ideas_json, format='json',path='storage/ideas/')
    print(f"New channel ideas saved at {channels_ideas}")
    
    return ideas_json

