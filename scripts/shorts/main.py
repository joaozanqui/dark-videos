import scripts.database as database
import scripts.utils.handle_text as handle_text
import scripts.shorts.ideas as ideas
import scripts.shorts.generate_script as generate_script
import scripts.audios.capcut as capcut
import scripts.video_build.generate as generate
import scripts.video_build.main as video_build
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
from scripts.audios.main import copy_audio_to_right_path
from scripts.shorts.utils import get_description
from moviepy.editor import *
import gc
import json
import os

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

def audios(channel_id):
    titles = database.channel_titles(channel_id)
    for title in titles:
        final_path = f"storage/{channel_id}/{title['title_number']}"
        video = database.get_item('videos', title['id'], 'title_id')
        
        print(f"\t-({channel_id}/{title['title_number']}) {title['title']}")
        all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')

        for shorts in all_shorts:
            if shorts['has_audio']:
                continue
            audio_file = capcut.run(shorts['full_script'])
            shorts_name = f"shorts_{shorts['number']}"
            audio_path = copy_audio_to_right_path(shorts_name, final_path, audio_file)

            if not audio_path:
                print("Error coping audio...")
                return None
            
            database.update('shorts', shorts['id'], 'has_audio', True)
            print(f"\t\t- Successful!: {audio_path}")

def build_infos(video, channel, title, shorts):
    variables = prompt_variables(video, channel, title)    
    idea = next((idea for idea in video['shorts_ideas'] if idea['id'] == shorts['number']), None)
    
    if idea:
        description = get_description(shorts['full_script'], idea, variables)
        database.update('shorts', shorts['id'], 'description', description)

def build(channel_id):
    channel = database.get_item('channels', channel_id)
    subtitles_top = channel['shorts_subtitles_position'] == 'top'

    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    for title in titles:
        video = database.get_item('videos', title['id'], 'title_id')
        final_path = f"storage/{channel_id}/{title['title_number']}"
        
        print(f"\t-({channel_id}/{title['title_number']}) {title['title']}")
        all_shorts = database.get_data('shorts', video['id'], column_to_compare='video_id')
        sorted_shorts = sorted(all_shorts, key=lambda k: k['number'])

        for shorts in sorted_shorts:
            if shorts['generated_device']:
                if not shorts['description']:
                    build_infos(video, channel, title, shorts)
                continue

            print(f"\t- Shorts {shorts['number']}...")

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
            expressions_path = f"assets/expressions/{channel_id}/chroma"
            expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration, position_h='center', position_v='center', expressions_size=1.9)            
            try:
                audio = video_build.create_audio(narration_audio, background_music)
                subtitles_h = 10 if subtitles_top else 1.5
                subtitles_w = 100
                video_composite = video_build.create_video(background_video_composite, expressions_images_composite, shorts['subtitles'], subtitles_padding=0.98, subtitles_denominators=(subtitles_w, subtitles_h))
                video_build.render_video(audio, video_composite, final_path, shorts_name)
                build_infos(video, channel, title, shorts)
                database.update('shorts', shorts['id'], 'generated_device', database.DEVICE)
            finally:
                print("\t- Cleaning up memory before next iteration...")
                collected_objects = gc.collect()
                print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
                print("-" * 40)


def run(channel_id):
    print("--- Building Shorts ---\n")
    channel = database.get_item('channels', channel_id)

    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    for title in titles:
        print(f"\t-({channel_id}/{title['title_number']}) {title['title']}")
        video = database.get_item('videos', title['id'], 'title_id')
        final_path = f"storage/{channel['id']}/{title['title_number']}"

        variables = prompt_variables(video, channel, title)
        video['shorts_ideas'] = ideas.run(video, variables)
        
        print("\t\t- Generating Shorts Scripts...")
        for idea in video['shorts_ideas']:
            generate_script.run(video, idea, variables, final_path)

        print("\t\t- Done!")
        