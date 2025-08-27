import scripts.utils.inputs as inputs

def outside_container(action):
    import outside_container_steps as outside_container_steps

    channel = inputs.select_from_data('channels')

    if action == 7:
        outside_container_steps.audios(channel['id'])
    elif action == 8:
        outside_container_steps.images(channel['id'])
    elif action == 10:
        outside_container_steps.upload(channel['id'])

def inside_container(action):
    import scripts.channel_analysis.main as channel_analysis
    import scripts.storytelling.main as storytelling
    import scripts.config.prompts as prompts
    import scripts.config.variables as handle_variables
    import scripts.ideas.main as ideas
    import scripts.ideas.titles as titles
    import scripts.video_build.main as video_build
    import scripts.cleaner as cleaner
    from scripts.database import backup

    if action == 1:
        channel_analysis.run_full_analysis_pipeline() 
    elif action == 11:
        cleaner.run()  
    elif action == 12:            
        backup()
    else:
        channel = inputs.select_from_data('channels')           

        if action <= 4:
            analysis = inputs.select_from_data('analysis')

            if action == 2:
                ideas.run(analysis)
            else:
                channel['analysis_id'] = analysis['id']

                if action == 3:
                    handle_variables.run(channel, analysis)
                elif action == 4:
                    titles.build_title_prompt(channel, analysis)
                    prompts.run(channel['id'], step='agents')
                    prompts.run(channel['id'], step='script')     
        elif action == 5:
            titles.run(channel['id'])
        elif action == 6:
            storytelling.run(channel['id'])
        elif action == 9:
            video_build.run(channel['id'], preprocess=True)
            video_build.run(channel['id'])

def run_process():
    actions = {
        1: "Analyse Example Channel",
        2: "Create Channels",
        3: "Create Variables",
        4: "Build Prompts",
        5: "Create Titles",
        6: "Create Scripts",
        7: "Generate Audios (OUTSIDE CONTAINER)", # outside
        8: "Download Images (OUTSIDE CONTAINER)", # outside
        9: "Build Videos",
        10: "Upload",
        11: "Clean uploaded Files",
        12: "Download Database Backup",
        0: "Exit",
    }
    
    action = -1
    while action != 0:
        for key, act in actions.items():
            print(f"{key} - {act}")

        while action < 1 or action > len(actions):
            action = int(input(f"\t-> "))

        if action == 7 or action == 8 or action == 10:
            outside_container(action)
        else:
            inside_container(action)
        
        action = -1

if __name__ == "__main__":
    run_process()