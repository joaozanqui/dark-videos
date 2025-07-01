import scripts.channel_analysis.main as channel_analysis
import scripts.storytelling.main as storytelling
import scripts.ideas.main as ideas
import scripts.images.main as images
import scripts.audios.main as audios
import scripts.video_build.main as video_build

if __name__ == "__main__":
    actions = {
        "1": "Analyse Channel",
        "2": "Generate Channels and Titles",
        "3": "Generate Script and Prompts",
        "4": "Download Images",
        "5": "Generate Audios",
        "6": "Build Videos"
    }

    input = 5

    if input == 1:
        insights_p1, insights_p2, insights_p3 =  channel_analysis.run_full_analysis_pipeline()
    else:
        with open('storage/analysis/insights_p1.txt', "r", encoding="utf-8") as file:
            insights_p1 = file.read() 
        with open('storage/analysis/insights_p2.txt', "r", encoding="utf-8") as file:
            insights_p2 = file.read() 
        with open('storage/analysis/insights_p3.txt', "r", encoding="utf-8") as file:
            insights_p3 = file.read()      

    if input == 2:
        ideas.run(insights_p1, insights_p2, insights_p3)
    elif input == 3:
        storytelling.run()
    elif input == 4:
        images.run()
    elif input == 5:
        audios.run()
    elif input == 6:
        video_build.run()

        