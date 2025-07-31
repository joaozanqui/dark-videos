import json
import scripts.database as database
import scripts.utils.gemini as gemini
import re

def is_preset_channel_config():
    yes_or_no = input("Is there a channel idea preset?\n1 -> Yes\n2 -> No\n ->")
    while yes_or_no != '1' and yes_or_no != '2':
        yes_or_no = input("Please select a valid option\n ->")
    
    return True if int(yes_or_no) == 1 else False 

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
    return database.build_prompt('ideas', prompt_file, variables)

def run(insights_p1, insights_p2, insights_p3, analysis_id, next_channel_id):   
    language = database.get_input_final_language()
    prompt = new_channel_ideas_prompt(insights_p1, insights_p2, insights_p3, language)   
    channels = gemini.run(prompt_text=prompt)
    
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
