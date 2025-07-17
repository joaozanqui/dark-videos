import scripts.channel_analysis.main as channel_analysis
import scripts.storytelling.main as storytelling
import scripts.ideas.main as ideas
import scripts.images.main as images
import scripts.audios.main as audios
import scripts.video_build.main as video_build
import json

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
    
    return str(action-1)

def run_process():
    actions = [
        "Analyse Channel and Generate Channels and Titles",
        "Generate Script and Prompts",
        "Download Images",
        "Generate Audios",
        "Build Videos"
    ]
    
    action = 0
    print("Actions:\n")
    while action < 1 or action > 6:
        for i, act in enumerate(actions):
            print(f"{i + 1} - {act}")
        action = int(input(f"\t-> "))

    if action == 1:
        insights_p1, insights_p2, insights_p3, analysis_id =  channel_analysis.run_full_analysis_pipeline()
        ideas.run(insights_p1, insights_p2, insights_p3, analysis_id)
    else:
        channel_id = select_channel()
        with open(f"storage/ideas/channels/{channel_id}/analysis.txt", "r", encoding="utf-8") as file:
            analysis_id = file.read()
        with open(f'storage/analysis/{analysis_id}/insights_p1.txt', "r", encoding="utf-8") as file:
            insights_p1 = file.read() 
        with open(f'storage/analysis/{analysis_id}/insights_p2.txt', "r", encoding="utf-8") as file:
            insights_p2 = file.read() 
        with open(f'storage/analysis/{analysis_id}/insights_p3.txt', "r", encoding="utf-8") as file:
            insights_p3 = file.read()      

    if action == 2:
        storytelling.run(channel_id)
    elif action == 3:
        images.run(channel_id)
    elif action == 4:
        audios.run(channel_id)
    elif action == 5:
        video_build.run(channel_id)

if __name__ == "__main__":
    run_process()