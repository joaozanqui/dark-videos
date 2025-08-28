import scripts.database as database
import config.keys as keys
import scripts.utils.handle_text as handle_text
import scripts.shorts.ideas as ideas
import scripts.shorts.generate_script as generate_script
import scripts.video_build.generate as generate
import scripts.video_build.main as video_build
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
from scripts.shorts.utils import get_description
from moviepy.editor import *
import gc
import json

def prompt_variables(video, channel, title):
    variables = database.channel_variables(channel['id'])
    
    return {
        "VIDEO_TITLE": handle_text.sanitize(title['title']),
        "RATIONALE": handle_text.sanitize(title['rationale']),
        "DESCRIPTION": handle_text.sanitize(video['description']),
        "FULL_SCRIPT": handle_text.sanitize(video['full_script']),
        "LANGUAGE": handle_text.sanitize(variables['LANGUAGE_AND_REGION']),
        "TOPICS": handle_text.sanitize(json.dumps(video['topics'], indent=2, ensure_ascii=False)),
        "CHANNEL_NAME": handle_text.sanitize(channel['name']),
        "SHORTS_QTY": channel['video_shorts_qty']
    }

def build_infos(video, channel, title, shorts):
    variables = prompt_variables(video, channel, title)    
    idea = next((idea for idea in video['shorts_ideas'] if idea['id'] == shorts['number']), None)
    
    if idea:
        description = get_description(shorts['full_script'], idea, variables)
        database.update('shorts', shorts['id'], 'description', description)


def create(channel, title):
    video = database.get_item('videos', title['id'], 'title_id')
    all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')
    
    if all_shorts:
        scripts = [shorts['full_script'] for shorts in all_shorts]
        uploaded = [shorts['uploaded'] for shorts in all_shorts]
        if all(scripts) or all(uploaded):
            return

    print(f"\t\t - Shorts Ideas for {title['title_number']}")
    
    variables = prompt_variables(video, channel, title)
    video['shorts_ideas'] = ideas.run(video, variables)
    
    print("\t\t - Generating Shorts Scripts...")
    for idea in video['shorts_ideas']:
        generate_script.run(video, idea, variables)

    print("\t\t - Shorts ideas Done!")

def run_preprocess(audio_path, temp_audio_path, channel, shorts):
    if database.has_file(temp_audio_path) and shorts['subtitles'] and shorts['expressions']:
        return False
    
    print(f"\t\t--- Preparing Shorts {shorts['id']} ---\n")
    
    if not database.has_file(temp_audio_path):
        video_build.remove_pauses(audio_path, temp_audio_path)

    if not shorts['subtitles']:
        language = database.get_item('languages', channel['language_id'])
        shorts['subtitles'] = generate.subtitles(temp_audio_path, language['name'], shorts['id'], table='shorts')

    if not shorts['expressions']:
        shorts['expressions'] = generate.expressions(shorts['subtitles'], channel['id'], shorts['id'], table='shorts')
    
    return True

def build_video(narration_audio, channel, shorts):
    subtitles = video_build.fix_subtitles_time(shorts['expressions'])
    expressions_path = f"assets/expressions/{channel['id']}/chroma"
    expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration, position_h='center', position_v='center', expressions_size=1.9)            
    
    subtitles_top = channel['shorts_subtitles_position'] == 'top'
    subtitles_h = 10 if subtitles_top else 1.5
    subtitles_w = 100
    background_video_composite = background_video.run(narration_audio.duration, video_orientation='vertical', target_resolution=(1080, 1920))
    
    video_composite = video_build.create_video(background_video_composite, expressions_images_composite, shorts['subtitles'], subtitles_padding=0.98, subtitles_denominators=(subtitles_w, subtitles_h))
    return video_composite

def build(temp_audio_path, channel, shorts, final_path, shorts_name):
    print(f"\t\t--- Bulding Shorts {shorts['number']} ---\n")

    narration_audio = video_build.get_narration_audio(temp_audio_path)
    video_composite = build_video(narration_audio, channel, shorts)   
    background_music = generate.music(audio_duration=narration_audio.duration ,mood=channel['mood'])
    audio = video_build.create_audio(narration_audio, background_music)
    
    video_build.render_video(audio, video_composite, final_path, shorts_name)
    database.update('shorts', shorts['id'], 'generated_device', keys.DEVICE)

def run(video, channel, title, preprocess=False):
    final_path = f"storage/{channel['id']}/{title['title_number']}"
    all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')
    sorted_shorts = sorted(all_shorts, key=lambda k: k['number'])
    all_shorts_device = [s['generated_device'] for s in all_shorts]

    if all(all_shorts_device):
        print(f"\t\t- Shorts Done!")
        return
    
    shorts_count = 0
    for shorts in sorted_shorts:
        if shorts['generated_device']:
            if not shorts['description']:
                build_infos(video, channel, title, shorts)
            continue
        
        shorts_name = f"shorts_{shorts['number']}"
        audio_path = f"{final_path}/{shorts_name}.mp3"    
        temp_audio_path = f"{final_path}/resized_audio_{shorts_name}.mp3"
        
        is_preprocessed = False
        try:
            if preprocess:
                is_preprocessed = run_preprocess(audio_path, temp_audio_path, channel, shorts)
                if not is_preprocessed:
                    shorts_count += 1
                if shorts_count == len(sorted_shorts):
                    print(f"\t\tShorts Preprocess done!")
            else:
                build(temp_audio_path, channel, shorts, final_path, shorts_name)
                build_infos(video, channel, title, shorts)

        finally:
            if is_preprocessed or not preprocess:
                collected_objects = gc.collect()
                print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
