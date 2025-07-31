
import scripts.ideas.new_channel as new_channel 
import scripts.utils.gemini as gemini
from string import Template
import os
import scripts.database as database

def build_prompt_template(channel, insights_p1, insights_p2, step):
    file_name = f"channel-{step}.txt"
    prompt_template = database.get_prompt_template('ideas', file_name)
    template = Template(prompt_template)

    variables = {
        "CHANNEL": channel,
        "INSIGHTS_P1": insights_p1,
        "INSIGHTS_P2": insights_p2
    }
    
    prompt = template.safe_substitute(variables)
    return prompt

def get_channel_info_prompt(channel, insights_p1, insights_p2, model, step):
    prompt = build_prompt_template(channel, insights_p1, insights_p2, step)
    response = gemini.run(prompt_text=prompt, gemini_model=model)
    
    if not response:
        return None
    
    return response

def run(insights_p1, insights_p2, insights_p3, analysis_id):
    gemini_model = gemini.get_model()

    if insights_p1 and insights_p2 and insights_p3:
        print("\n--- Generating Viral Channel and Videos Ideas (using Gemini) ---")

        old_channels = database.get_channels()

        next_channel_id = max(channel["id"] for channel in old_channels) + 1 if len(old_channels) else 1

        new_channels = new_channel.run(insights_p1, insights_p2, insights_p3, analysis_id, next_channel_id, gemini_model)
        old_channels.extend(new_channels)

        channels_ideas = database.export('channels', old_channels, format='json',path='storage/ideas/')
        print(f"New channel ideas saved at {channels_ideas}")

        for i, channel in enumerate(new_channels):
            channel_id = i + next_channel_id
            images_prompt_path = f"storage/ideas/channels/{channel_id}/"

            for step in ["logo", "profile", "banner", "description"]:
                if not os.path.exists(f"{images_prompt_path}{step}.txt"):
                    prompt = get_channel_info_prompt(channel, insights_p1, insights_p2, gemini_model, step=step)
                    if not prompt: 
                        return None
                    database.export(step, prompt, path=images_prompt_path)
    else:
        print("\nSkipping as not all preceding insights are available.")
        return {}
    