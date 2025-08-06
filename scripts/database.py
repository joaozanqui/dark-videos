import json
import os
from string import Template
import scripts.utils.handle_text as handle_text

ALLOWED_IMAGES_EXTENSIONS = ['jpg', 'png', 'jpeg']

def export(file_name: str, data: str|list, format='txt', path='storage/') -> str:
    try:
        if path[-1] != '/':
            path += '/'
            
        os.makedirs(path, exist_ok=True)
        export_path = f"{path}{file_name}.{format}"
        with open(export_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, ensure_ascii=False, indent=4)
            elif format == 'srt':
                for i, segment in enumerate(data):
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment['text'].strip()

                    start_subtitiles = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02},{int(start_time%1*1000):03}"
                    end_subtitles = f"{int(end_time//3600):02}:{int(end_time%3600//60):02}:{int(end_time%60):02},{int(end_time%1*1000):03}"

                    f.write(f"{i + 1}\n")
                    f.write(f"{start_subtitiles} --> {end_subtitles}\n")
                    f.write(f"{text}\n\n")
            else:
                f.write(data)
        
        return export_path
    except Exception as e:
        print(f"Error exporting {file_name}: {e}")
        return None

def exists(file):
    return os.path.exists(file)

def get_json_data(path):
    if not exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    return data

def get_txt_data(path):
    if not exists(path):
        return []
    
    with open(path, "r", encoding="utf-8") as file:
        data = file.read()
    
    return data

def get_titles(channel_id):
    path = f"storage/ideas/titles/{str(channel_id)}.json"
    titles = get_json_data(path)

    return titles

def get_channels():
    path = "storage/ideas/channels.json"
    channels = get_json_data(path)

    return channels

def get_input_data():
    path = 'config/data.json'
    data = get_json_data(path)
    
    return data

def get_variables(channel_id):
    path = f"storage/thought/{str(channel_id)}/variables.json"
    variables = get_json_data(path)
    
    return handle_text.sanitize_variables(variables)

def get_analysis(analysis_id, phase):
    path = f'storage/analysis/{str(analysis_id)}/insights_p{str(phase)}.txt'
    insights = get_txt_data(path)
    
    return insights

def get_topics(channel_id, title_id):
    path = f"storage/thought/{str(channel_id)}/{str(title_id)}/topics.json"
    topics = get_json_data(path)
    
    return topics

def get_full_script(channel_id, title_id, file_name='full_script', shorts=False):
    middle_path = "shorts" if shorts else "thought" 
    path = f"storage/{middle_path}/{channel_id}/{title_id}/{file_name}.txt"
    full_script = get_txt_data(path)
    
    return full_script

def get_prompt_template(step, file):
    txt_steps = [
        'ideas',
        'analysis'
    ]
    
    format = 'txt' if step in txt_steps else 'json'
    path = f"default_prompts/{str(step)}/{str(file)}.{format}"
    prompt = get_txt_data(path)
    
    return prompt

def build_prompt(step, file_name, variables, send_as_json=False):
    sanitized_variables = handle_text.sanitize_variables(variables)
    prompt_template = get_prompt_template(step, file_name)
    template = Template(prompt_template)
    prompt = template.safe_substitute(sanitized_variables)

    if send_as_json:
        prompt_json = json.loads(prompt)
        prompt = json.dumps(prompt_json, indent=2, ensure_ascii=False)
    
    return prompt

def get_prompt_file(channel_id, step='', file=''):
    if not file:
        return ''
    
    path = f"storage/prompts/{str(channel_id)}/{step}{'/' if step else ''}{str(file)}.json"
    prompt = get_txt_data(path)
    
    return prompt

def get_subtitles(channel_id, title_id, file_name='subtitles', shorts=False):
    middle_path = "shorts" if shorts else "thought" 
    path = f"storage/{middle_path}/{channel_id}/{title_id}/{file_name}.srt"
    subtitles = get_txt_data(path)
    
    return subtitles

def get_expressions(channel_id, title_id, file_name='expressions', shorts=False):
    middle_path = "shorts" if shorts else "thought" 
    path = f"storage/{middle_path}/{channel_id}/{title_id}/{file_name}.json"
    expressions = get_json_data(path)
    
    return expressions

def get_video_description(channel_id, title_id):
    path = f"storage/thought/{channel_id}/{title_id}/description.txt"
    description = get_txt_data(path)

    return description

def get_thumbnail_data(channel_id, title_id):
    path = f"storage/thought/{channel_id}/{title_id}/thumbnail_data.json"
    data = get_json_data(path)
    
    return data

def get_thumbnail_prompt(channel_id, title_id):
    path = f"storage/thought/{channel_id}/{title_id}/thumbnail_prompt.txt"
    prompt = get_txt_data(path)
    
    return prompt

def get_channel_by_id(channel_id):
    channels = get_channels()
    return channels[int(channel_id)-1]

def update_channels(channel):
    channels = get_channels()
    for index, current_channel in enumerate(channels):
        if current_channel.get('id') == channel['id']:
            channels[index] = channel
            break
    
    export('channels', channels, format='json', path='storage/ideas/')
    return channels

def get_input_final_language():
    data = get_input_data()
    language = data['final_language']

    if not language:
        language = 'english'

    return language

def get_input_video_duration():
    data = get_input_data()  
    duration = data['duration']

    if not duration:
        duration = 20

    return duration

def get_input_channel_url():
    data = get_input_data()    
    channel_url_or_id = data['channel_to_copy']

    if not channel_url_or_id:
        print("No channel URL or ID provided. Exiting.")
        return None

    return channel_url_or_id

def get_assets_allowed_expressions(channel_id, is_video=False):
    path = f"assets/expressions/{str(channel_id)}/{'chroma' if is_video else 'transparent'}"
    allowed_expressions = []
    for expression in os.listdir(path):
        full_path = os.path.join(path, expression)
        if os.path.isfile(full_path):
            allowed_expressions.append(expression.split('.')[0])
    
    return allowed_expressions

def get_shorts_ideas(channel_id, title_id):
    path = f"storage/shorts/{str(channel_id)}/{str(title_id)}/shorts_ideas.json"
    ideas = get_json_data(path)
    
    return ideas