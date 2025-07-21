import scripts.channel_analysis.main as channel_analysis
import scripts.storytelling.main as storytelling
import scripts.config.prompts as prompts
import scripts.config.variables as handle_variables
import scripts.ideas.main as ideas
import scripts.config.titles as titles
import scripts.images.main as images
import scripts.audios.main as audios
import scripts.video_build.main as video_build
from scripts.utils import get_variables
import json
import os
import re

def select_analysed_channel():
    analysis_path = "storage/analysis"
    analysis_folders = [
        os.path.join(analysis_path, analysis) for analysis in os.listdir(analysis_path)
        if os.path.isdir(os.path.join(analysis_path, analysis)) and analysis.isdigit()
    ]
    analysis_folders.sort()

    channels = []
    for path in analysis_folders:
        file = os.path.join(path, 'insights_p1.txt')
        with open(file, "r", encoding="utf-8") as file:
            insights = file.read()

        first_line = insights.splitlines()[0]
        match = re.search(r"(?<!here)s?'(.*?)'", first_line, re.IGNORECASE)

        channel = match.group(1) if match else f"Channel {path}"
        channels.append(channel)

    max = 0
    print("\n\nAnalysed Channels:\n")
    for i, channel in enumerate(channels):
        print(f"{i+1} - {channel}")
        max = i+1
    action = 0
    while action < 1 or action > max:
        action = int(input(f"\t-> "))
    
    return str(action-1)


def select_channel():
    channels_path = "storage/ideas/channels.json"

    with open(channels_path, "r", encoding="utf-8") as file:
        channels = json.load(file)
    
    max = 0
    print("\n\nChannels:\n")
    for i, channel in enumerate(channels):
        print(f"{i+1} - {channel['name']}")
        max = i+1

    action = 0
    while action < 1 or action > max:
        action = int(input(f"\t-> "))
    
    channel_id = action-1
    channel_chosen = channels[channel_id]
    return channel_chosen

def get_insights(analysis_id):
    with open(f'storage/analysis/{analysis_id}/insights_p1.txt', "r", encoding="utf-8") as file:
        insights_p1 = file.read() 
    with open(f'storage/analysis/{analysis_id}/insights_p2.txt', "r", encoding="utf-8") as file:
        insights_p2 = file.read() 
    with open(f'storage/analysis/{analysis_id}/insights_p3.txt', "r", encoding="utf-8") as file:
        insights_p3 = file.read()    

    return insights_p1, insights_p2, insights_p3

def run_process():
    actions = [
        "Analyse Example Channel",
        "Create Channels",
        "Create Variables",
        "Build Titles Prompt",
        "Create Titles",
        "Build Agents Prompts",
        "Build Scripts Prompts",
        "Create Scripts",
        "Download Images",
        "Generate Audios",
        "Build Videos"
    ]
    
    action = 0
    print("Actions:\n")
    while action < 1 or action > 11:
        for i, act in enumerate(actions):
            print(f"{i + 1} - {act}")
        action = int(input(f"\t-> "))

    if action == 1:
        channel_analysis.run_full_analysis_pipeline()
    elif action == 2:
        analysis_id = select_analysed_channel()
        insights_p1, insights_p2, insights_p3 = get_insights(analysis_id)

        ideas.run(insights_p1, insights_p2, insights_p3, analysis_id)
    else:
        channel = select_channel()           
        insights_p1, insights_p2, insights_p3 = get_insights(channel['analysis'])


        if action == 3:
            handle_variables.run(channel, insights_p1, insights_p2, insights_p3)
        else:
            variables = get_variables(channel['id'])
            if action == 4:
                titles.build_prompt(insights_p1, insights_p2, insights_p3, channel, variables)
            if action == 5:
                titles.run(channel['id'])
            elif action == 6:
                prompts.run(channel['id'], variables, step='agents')
            elif action == 7:
                prompts.run(channel['id'], variables, step='script')
            elif action == 8:
                storytelling.run(channel['id'])
            elif action == 9:
                images.run(channel['id'])
            elif action == 10:
                audios.run(channel['id'])
            elif action == 11:
                video_build.run(channel['id'])

if __name__ == "__main__":
    run_process()