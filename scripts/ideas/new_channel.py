import json
import scripts.database as database
import scripts.utils.gemini as gemini
import scripts.utils.inputs as inputs
import re
    
def get_video_duration():
    duration = input("\t- Each video duration (minutes) -> ")
    try:
        return int(duration)
    except Exception as e:
        print(f"\t\t- Please provide a valid INTEGER number...")
        return get_video_duration()
    

def new_channel_ideas_prompt(analysis: dict, language: str) -> str :   
    variables = {
        "phase1_insights": analysis['insights_p1'],
        "phase2_insights": analysis['insights_p2'],
        "phase3_insights": analysis['insights_p3'],
        "language": language
    }

    prompt_title = "preset-channel-idea" if inputs.yes_or_no(f"\t- Is there a channel idea preset?") else "new-channels-ideas"
    return database.get_prompt_template('ideas', prompt_title, variables)

def run(analysis):   
    duration = get_video_duration()
    language = inputs.select_from_data('languages')
    prompt = new_channel_ideas_prompt(analysis, language['name'])   
    channels = gemini.run(prompt_json=prompt)
    
    if not channels:
        print("Failed to generate channels ideas")
        return None
    
    try:
        channels_clean = re.sub(r'^```json\n|```$', '', channels.strip())
        channels_json = json.loads(channels_clean)
        for channel in channels_json:
            channel['analysis_id'] = analysis['id'] 
            channel['videos_duration'] = duration
            channel['shorts_subtitles_position'] = 'top'
            channel['language_id'] = language['id']
            channel['upload_url'] = 'https://studio.youtube.com/channel/'
    except json.JSONDecodeError as e:
        print(f"Error decode JSON: {e}")
        return None

    print("\nGenerated Viral Channels Ideas (for your new agent/scripts).")
    
    return channels_json
