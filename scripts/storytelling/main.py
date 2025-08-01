import scripts.database as database
import scripts.storytelling.generate_script as generate_script
import scripts.storytelling.generate_infos as generate_infos
import scripts.storytelling.generate_topics as generate_topics
from string import Template
import os 

def run(channel_id):
    channel = database.get_channel_by_id(channel_id)

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    variables = database.get_variables(channel_id)
    topics_agent_prompt = database.get_prompt_file(channel_id, step='agents',file='topics')
    script_agent_prompt = database.get_prompt_file(channel_id, step='agents',file='script')
    topics_prompt = database.get_prompt_file(channel_id, step='script',file='topics')
    topics_template_prompt = Template(topics_prompt)
    script_prompt = database.get_prompt_file(channel_id, step='script',file='script')
    script_template_prompt = Template(script_prompt)

    if not variables or not topics_agent_prompt or not script_agent_prompt or not topics_template_prompt or not script_template_prompt:
        return []
    
    for title_id, title in enumerate(titles):
        video_path = f"storage/thought/{channel_id}/{title_id}/"
        
        has_topics = os.path.exists(f"{video_path}topics.json") or os.path.exists(f"{video_path}topics.txt")
        has_full_script = os.path.exists(f"{video_path}full_script.txt")
        has_all_files = has_topics and  has_full_script
        
        if has_all_files:
            continue

        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        variables['VIDEO_TITLE'] =  title['title']
        variables['RATIONALE'] =  title['rationale']

        if not has_topics:
            print(f"\t\t - Topics...")
            variables['TOPICS'] = generate_topics.run(variables, topics_template_prompt, topics_agent_prompt)
            if not variables['TOPICS']:
                return run(channel_id)
            database.export('topics', variables['TOPICS'], format='json', path=video_path)
            if isinstance(variables['TOPICS'], list):
                variables['TOPICS'] = variables['TOPICS'][0]
        else:
            variables['TOPICS'] = database.get_topics(channel_id, title_id)

        if not has_full_script:
            print(f"\t\t - Full script...")
            full_script = generate_script.run(variables, script_agent_prompt, channel_id, title_id, script_template_prompt)
        else:
            full_script = database.get_full_script(channel_id, title_id)
        
        if full_script:
            generate_infos.run(channel_id, title_id, video_path, variables)
    
        print(f"\t\t - Done!")
    return