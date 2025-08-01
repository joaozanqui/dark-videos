import scripts.channel_analysis.main as channel_analysis
import scripts.storytelling.main as storytelling
import scripts.config.prompts as prompts
import scripts.config.variables as handle_variables
import scripts.ideas.main as ideas
import scripts.config.titles as titles
import scripts.images.main as images
import scripts.images.thumbnail as thumbnail
import scripts.audios.main as audios
import scripts.video_build.main as video_build
import scripts.shorts.main as shorts
import scripts.database as database
import os
import re

def select_analysed_channel():
    analysis_path = "storage/analysis"

    analysis_folders = []
    for analysis in os.listdir(analysis_path):
        full_path = os.path.join(analysis_path, analysis)
        if os.path.isdir(full_path):
            analysis_folders.append(analysis) 
    analysis_folders.sort()

    channels = []
    for analysis_id in analysis_folders:
        insights_p1 = database.get_analysis(analysis_id, 1)
        first_line = insights_p1.splitlines()[0]
        match = re.search(r"(?<!here)s?'(.*?)'", first_line, re.IGNORECASE)
        if not match:
            match = re.search(r'(?<!here)s?"(.*?)"', first_line, re.IGNORECASE)

        channel = match.group(1) if match else f"Channel {analysis_id}"
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
    channels = database.get_channels()
    
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
        "Build Thumbnail",
        "Generate Audios",
        "Build Videos",
        "Create Shorts Ideas",
        "Generate Shorts Audios",
        "Build Shorts",
    ]
    
    action = 0
    print("Actions:\n")
    while action < 1 or action > len(actions):
        for i, act in enumerate(actions):
            print(f"{i + 1} - {act}")
        action = int(input(f"\t-> "))

    if action == 1:
        channel_analysis.run_full_analysis_pipeline()
    else:        
        if action == 2:
            analysis_id = select_analysed_channel()
            insights_p1 = database.get_analysis(analysis_id, 1)
            insights_p2 = database.get_analysis(analysis_id, 2)
            insights_p3 = database.get_analysis(analysis_id, 3)

            ideas.run(insights_p1, insights_p2, insights_p3, analysis_id)
        else:
            channel = select_channel()           
            analysis_id = channel['analysis']

            insights_p1 = database.get_analysis(analysis_id, 1)
            insights_p2 = database.get_analysis(analysis_id, 2)
            insights_p3 = database.get_analysis(analysis_id, 3)

            if action == 3:
                handle_variables.run(channel, insights_p1, insights_p2, insights_p3)
            else:
                if action == 4:
                    titles.build_title_prompt(insights_p1, insights_p2, insights_p3, channel)
                if action == 5:
                    titles.run(channel['id'])
                elif action == 6:
                    prompts.run(channel['id'], step='agents')
                elif action == 7:
                    prompts.run(channel['id'], step='script')
                elif action == 8:
                    storytelling.run(channel['id'])
                elif action == 9:
                    images.run(channel['id'])
                elif action == 10:
                    thumbnail.run(channel['id'])
                elif action == 11:
                    audios.run(channel['id'])
                elif action == 12:
                    video_build.run(channel['id'])
                elif action == 13:
                    shorts.run(channel['id'])
                elif action == 14:
                    shorts.audios(channel['id'])
                elif action == 15:
                    shorts.build(channel['id'])

if __name__ == "__main__":
    run_process()