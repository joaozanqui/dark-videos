import scripts.database as database
import scripts.storytelling.generate_script as generate_script
import scripts.storytelling.generate_infos as generate_infos
import scripts.storytelling.generate_topics as generate_topics
import scripts.shorts.main as shorts

def handle_video_data(title_id: int):
    video_data = database.get_item('videos', title_id, column_to_compare='title_id')
    
    if not video_data:
        return database.insert({"title_id": title_id}, 'videos')
    
    return video_data

def handle_topics(video_data: dict, channel_id: int, variables: dict):
    if video_data['topics']:
        return video_data['topics']

    print(f"\t\t - Topics...")
    topics_agent_prompt = database.get_prompt_file(channel_id, 'agents_topics')
    topics_template_prompt = database.get_prompt_file(channel_id, 'script_topics')
    
    if not topics_agent_prompt or not topics_template_prompt:
        return {}

    topics = generate_topics.run(variables, topics_template_prompt, str(topics_agent_prompt))

    if not topics:
        return handle_topics(video_data, channel_id, variables)
    
    database.update('videos', video_data['id'], 'topics', topics)

    return topics

def handle_full_script(video_data: dict, channel_id: int, variables: dict):
    if video_data['full_script']:
        return video_data['full_script']
    
    print(f"\t\t - Full script...")
    script_agent_prompt = database.get_prompt_file(channel_id, 'agents_script')
    script_template_prompt = database.get_prompt_file(channel_id, 'script_script')

    if not script_agent_prompt or not script_template_prompt:
        return ''

    full_script = generate_script.run(variables, str(script_agent_prompt), script_template_prompt)
    
    if not full_script:
        return handle_full_script(video_data, channel_id, variables)
    
    database.update('videos', video_data['id'], 'full_script', full_script)

    return full_script


def run(channel_id: int):
    channel = database.get_item('channels', channel_id)

    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    variables = database.channel_variables(channel_id)
    if not variables:
        return False
    

    last_expressions = []
    for title in titles:
        video_data = handle_video_data(title['id'])

        if video_data['topics'] and video_data['full_script'] and video_data['description'] and video_data['thumbnail_data'] and video_data['thumbnail_prompt']:
            continue

        print(f"\t-(Channel {channel_id} / Title {title['title_number']}) {title['title']}")
        variables['VIDEO_TITLE'] =  title['title']
        variables['RATIONALE'] =  title['rationale']
        variables['TOPICS'] = handle_topics(video_data, channel_id, variables)
        if not variables['TOPICS']:
            return False
        variables['FULL_SCRIPT'] = handle_full_script(video_data, channel_id, variables)
        if not variables['FULL_SCRIPT']:
            return False
        
        variables['LAST_THUMBNAIL_EXPRESSIONS'] = last_expressions
        thumbnail_expression = generate_infos.run(video_data, variables)
        last_expressions.append(thumbnail_expression)

        shorts.create(channel, title)
        
        print(f"\t\t - Done!")

    return True