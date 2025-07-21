from scripts.utils import get_prompt, analyze_with_gemini, get_final_language
import json
import re

def is_preset_channel_config():
    yes_or_no = input("Is there a channel idea preset?\n1 -> Yes\n2 -> No\n ->")
    return yes_or_no

def new_channel_ideas_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    language: str,
) -> str :
    variables = {
        "phase1_insights": phase1_insights,
        "phase2_insights": phase2_insights,
        "phase3_insights": phase3_insights,
        "language": language
    }

    prompt_file = "preset-channel-idea.txt" if is_preset_channel_config() else "new-channels-ideas.txt"

    prompt_path = f"scripts/ideas/prompts/{prompt_file}"
    return get_prompt(prompt_path, variables)

def run(insights_p1, insights_p2, insights_p3, analysis_id, next_channel_id, model):   
    language = get_final_language()
    prompt = new_channel_ideas_prompt(insights_p1, insights_p2, insights_p3, language)   
    channels = analyze_with_gemini(prompt_text=prompt, gemini_model=model)
    
    if not channels:
        print("Failed to generate channels ideas")
        return None
    
    try:
        channels_clean = re.sub(r'^```json\n|```$', '', channels.strip())
        channels_json = json.loads(channels_clean)
        for channel in channels_json:
            channel['id'] = int(next_channel_id)
            channel['analysis'] = int(analysis_id)
            next_channel_id += 1
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        return None

    print("\nGenerated Viral Channels Ideas (for your new agent/scripts).")
    
    return channels_json
