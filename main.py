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
    for i, channel in enumerate(channels):
        print(f"{i+1} - {channel['name']}")
        max = i+1

    input = 0
    while input < 1 and input > max:
        input = input(f"\t-> ")

def run_process(channel_id):
    actions = {
        "1": "Analyse Channel",
        "2": "Generate Channels and Titles",
        "3": "Generate Script and Prompts",
        "4": "Download Images",
        "5": "Generate Audios",
        "6": "Build Videos"
    }
    
    input = 0
    while input < 1 and input > 6:
        input = input(f"ACTIONS:\n{actions}\n\t-> ")

    if input == 1:
        insights_p1, insights_p2, insights_p3, analysis_id =  channel_analysis.run_full_analysis_pipeline()
    else:
        with open(f"storage/idas/channels/{channel_id}/analysis.txt", "r", encoding="utf-8") as file:
            analysis_id = file.read()
        with open(f'storage/analysis/{analysis_id}/insights_p1.txt', "r", encoding="utf-8") as file:
            insights_p1 = file.read() 
        with open(f'storage/analysis/{analysis_id}/insights_p2.txt', "r", encoding="utf-8") as file:
            insights_p2 = file.read() 
        with open(f'storage/analysis/{analysis_id}/insights_p3.txt', "r", encoding="utf-8") as file:
            insights_p3 = file.read()      

    if input == 2:
        ideas.run(insights_p1, insights_p2, insights_p3, analysis_id)
    elif input == 3:
        storytelling.run()
    elif input == 4:
        images.run()
    elif input == 5:
        audios.run()
    elif input == 6:
        video_build.run()

if __name__ == "__main__":
    run_process(input)