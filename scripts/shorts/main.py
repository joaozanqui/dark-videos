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

def build(channel, title, subtitles_top):
    video = database.get_item('videos', title['id'], 'title_id')
    final_path = f"storage/{channel['id']}/{title['title_number']}"
    
    print(f"\t\t- Shorts")
    all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')
    sorted_shorts = sorted(all_shorts, key=lambda k: k['number'])

    for shorts in sorted_shorts:
        if shorts['generated_device']:
            if not shorts['description']:
                build_infos(video, channel, title, shorts)
            continue

        print(f"\t\t- Shorts {shorts['number']}...")

        shorts_name = f"shorts_{shorts['number']}"
        audio_path = f"{final_path}/{shorts_name}.mp3"
        language = database.get_item('languages', channel['language_id'])

        if not shorts['subtitles']:
            shorts['subtitles'] = generate.subtitles(audio_path, language['name'], shorts['id'], table='shorts')
        if not shorts['expressions']:
            shorts['expressions'] = generate.expressions(shorts['subtitles'], channel['id'], shorts['id'], table='shorts')

        narration_audio = AudioFileClip(audio_path)
        background_music = generate.music(audio_duration=narration_audio.duration ,mood=channel['mood'])
        background_video_composite = background_video.run(narration_audio.duration, video_orientation='vertical', target_resolution=(1080, 1920))
        
        subtitles = video_build.fix_subtitles_time(shorts['expressions'])
        expressions_path = f"assets/expressions/{channel['id']}/chroma"
        expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration, position_h='center', position_v='center', expressions_size=1.9)            
        try:
            audio = video_build.create_audio(narration_audio, background_music)
            subtitles_h = 10 if subtitles_top else 1.5
            subtitles_w = 100
            video_composite = video_build.create_video(background_video_composite, expressions_images_composite, shorts['subtitles'], subtitles_padding=0.98, subtitles_denominators=(subtitles_w, subtitles_h))
            video_build.render_video(audio, video_composite, final_path, shorts_name)
            build_infos(video, channel, title, shorts)
            database.update('shorts', shorts['id'], 'generated_device', keys.DEVICE)
        finally:
            print("\t- Cleaning up memory before next iteration...")
            collected_objects = gc.collect()
            print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
            print("-" * 40)


def create(channel, title):
    video = database.get_item('videos', title['id'], 'title_id')
    all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')
    
    if all_shorts:
        scripts = [shorts['full_script'] for shorts in all_shorts]
        if all(scripts):
            return

    print(f"\t\t-Shorts Ideas video {video['id']}")
    
    variables = prompt_variables(video, channel, title)
    video['shorts_ideas'] = ideas.run(video, variables)
    
    print("\t\t- Generating Shorts Scripts...")
    for idea in video['shorts_ideas']:
        generate_script.run(video, idea, variables)

    print("\t\t- Shorts ideas Done!")
