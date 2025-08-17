import scripts.channel_analysis.main as channel_analysis
import scripts.storytelling.main as storytelling
import scripts.config.prompts as prompts
import scripts.config.variables as handle_variables
import scripts.ideas.main as ideas
import scripts.ideas.titles as titles
import scripts.images.main as images
import scripts.images.thumbnail as thumbnail
import scripts.audios.main as audios
import scripts.video_build.main as video_build
import scripts.upload.main as upload
import scripts.shorts.main as shorts
import scripts.database as database
import scripts.cleaner as cleaner
import scripts.utils.inputs as inputs

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
        "Upload",
        "Clean uploaded Files",
    ]
    
    action = 0
    print("Actions:\n")
    while action < 1 or action > len(actions):
        for i, act in enumerate(actions):
            print(f"{i + 1} - {act}")
        action = int(input(f"\t-> "))

    if action == 1:
        channel_analysis.run_full_analysis_pipeline()
    elif action >= 2 and action <= 8:
        analysis = inputs.select_from_data('analysis')
        
        if action == 2:
            ideas.run(analysis)
        else:
            channel = inputs.select_from_data('channels')           
            if action == 3:
                handle_variables.run(channel, analysis)
            elif action == 4:
                titles.build_title_prompt(channel, analysis)
            elif action == 5:
                titles.run(channel['id'])
            elif action == 6:
                prompts.run(channel['id'], step='agents')
            elif action == 7:
                prompts.run(channel['id'], step='script')
            elif action == 8:
                storytelling.run(channel['id'])
    elif action == 17:
        cleaner.run()        
    else:
        channel = inputs.select_from_data('channels')           
        analysis = database.get_item('analysis', value=channel['analysis_id'])

        if action == 9:
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
        elif action == 16:
            upload.run(channel['id'])


if __name__ == "__main__":
    run_process()