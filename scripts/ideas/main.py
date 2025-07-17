
import scripts.ideas.new_channel as new_channel 
import scripts.ideas.titles as titles
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

        with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
            old_channels = json.load(file) 
        next_channel_id = max(channel["id"] for channel in old_channels) + 1

        new_channels = new_channel.run(insights_p1, insights_p2, insights_p3, next_channel_id, gemini_model)
        old_channels.extend(new_channels)

        channels_ideas = export('channels', old_channels, format='json',path='storage/ideas/')
        print(f"New channel ideas saved at {channels_ideas}")

        for i, channel in enumerate(new_channels):
            channel_id = i + next_channel_id
            images_prompt_path = f"storage/ideas/channels/{channel_id}/"
            export('analysis', str(analysis_id), path=images_prompt_path)
            for step in ["logo", "profile", "banner", "description"]:
                if not os.path.exists(f"{images_prompt_path}{step}.txt"):
                    prompt = get_channel_info_prompt(channel, insights_p1, insights_p2, gemini_model, step=step)
                    if not prompt: 
                        return None
                    export(step, prompt, path=images_prompt_path)
            titles_ideas = titles.run(insights_p1, insights_p2, insights_p3, channel, gemini_model)
            title_ideas_path = export(f"{channel_id}", titles_ideas, format='json',path='storage/ideas/titles/')
            print(f"Title Ideas saved at {title_ideas_path}")

    else:
        print("\nSkipping as not all preceding insights are available.")
        return {}
    