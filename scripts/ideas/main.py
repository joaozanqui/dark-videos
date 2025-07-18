
import scripts.ideas.new_channel as new_channel 
from scripts.utils import get_gemini_model, analyze_with_gemini, export
import json
from string import Template
import os

def build_prompt_template(channel, insights_p1, insights_p2, step):
    template_path = f"scripts/ideas/prompts/"
    template_file = f"{template_path}channel-{step}.txt"

    with open(template_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()
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
    response = analyze_with_gemini(prompt, gemini_model=model)
    
    if not response:
        return None
    
    return response

def run(insights_p1, insights_p2, insights_p3, analysis_id):
    gemini_model = get_gemini_model()

    if insights_p1 and insights_p2 and insights_p3:
        print("\n--- Generating Viral Channel and Videos Ideas (using Gemini) ---")

        channels_path = 'storage/ideas'
        os.makedirs(channels_path, exist_ok=True)

        channels_file = f"{channels_path}/channels.json"
        if os.path.exists(channels_file):
            with open(channels_file, "r", encoding="utf-8") as file:
                old_channels = json.load(file) 
        else:
            old_channels = []

        next_channel_id = max(channel["id"] for channel in old_channels) + 1 if len(old_channels) else 1

        new_channels = new_channel.run(insights_p1, insights_p2, insights_p3, analysis_id, next_channel_id, gemini_model)
        old_channels.extend(new_channels)

        channels_ideas = export('channels', old_channels, format='json',path='storage/ideas/')
        print(f"New channel ideas saved at {channels_ideas}")

        for i, channel in enumerate(new_channels):
            channel_id = i + next_channel_id
            images_prompt_path = f"storage/ideas/channels/{channel_id}/"

            for step in ["logo", "profile", "banner", "description"]:
                if not os.path.exists(f"{images_prompt_path}{step}.txt"):
                    prompt = get_channel_info_prompt(channel, insights_p1, insights_p2, gemini_model, step=step)
                    if not prompt: 
                        return None
                    export(step, prompt, path=images_prompt_path)
    else:
        print("\nSkipping as not all preceding insights are available.")
        return {}
    