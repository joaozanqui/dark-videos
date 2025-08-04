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

def prompt_variables(channel_id, title_id, video_title):
    variables = database.get_variables(channel_id)
    topics_json = database.get_topics(channel_id, title_id)
    topics = handle_text.sanitize(json.dumps(topics_json['introduction'], indent=2, ensure_ascii=False))
    channel = database.get_channel_by_id(channel_id)
    
    return {
        "VIDEO_TITLE": handle_text.sanitize(video_title['title']),
        "RATIONALE": handle_text.sanitize(video_title['rationale']),
        "DESCRIPTION": handle_text.sanitize(database.get_video_description(channel_id, title_id)),
        "FULL_SCRIPT": handle_text.sanitize(database.get_full_script(channel_id, title_id)),
        "LANGUAGE": handle_text.sanitize(variables['LANGUAGE_AND_REGION']),
        "TOPICS": handle_text.sanitize(topics),
        "CHANNEL_NAME": handle_text.sanitize(channel['name']),
    }

def audios(channel_id):
    titles = database.get_titles(channel_id)
    for title_id, title in enumerate(titles):
        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        shorts_path = f"storage/shorts/{channel_id}/{title_id}"
        scripts = []
        if os.path.exists(shorts_path):
            for filename in os.listdir(shorts_path):
                if filename.endswith(".txt"):
                    scripts.append(filename)
        
        scripts.sort()
        for script_file in scripts:
            script_name = script_file.split('.')[0]
            script_path = f"{shorts_path}/{script_file}"
            
            output_audio_path = f"{shorts_path}/{script_name}.mp3"
            if database.exists(output_audio_path):
                continue

            script = database.get_txt_data(script_path)

            audio_file = capcut.run(script)
            audio_path = copy_audio_to_right_path(script_name, shorts_path, audio_file)

            if not audio_path:
                print("Error coping audio...")
                return None
            
            print(f"\t\t- Successful!: {audio_path}")

def build_infos(channel_id, title_id, title, script_name, final_path):
    ideas = database.get_shorts_ideas(channel_id, title_id)
    variables = prompt_variables(channel_id, title_id, title)

    script_id = script_name.split('_')[1]
    full_script = database.get_full_script(channel_id, title_id, file_name=script_name, shorts=True)
    idea = next((idea for idea in ideas if int(idea['id']) == int(script_id)), None)
    if idea:
        description = get_description(full_script, idea, variables)
        database.export(f"{script_name}_description", description, path=f"{final_path}/")

def build(channel_id):
    music_mood = "calm"
    channel = database.get_channel_by_id(channel_id)
    subtitles_top = channel['shorts_subtitles_position'] == 'top'

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    for title_id, title in enumerate(titles):
        final_path = f"storage/videos/{channel_id}/{title_id}"
        shorts_path = f"storage/shorts/{channel_id}/{title_id}"
        
        print(f"\t-({channel_id}/{title_id}) {title['title']}")

        scripts = []
        if os.path.exists(shorts_path):
            for filename in os.listdir(shorts_path):
                if filename.endswith(".mp3"):
                    scripts.append(filename)
        
        scripts.sort()
        for script_file in scripts:
            script_name = script_file.split('.')[0]

            print(f"\t- {script_name}")
            audio_path = f"{shorts_path}/{script_name}.mp3"
            output_video_path = f"{final_path}/{script_name}.mp4"
            output_text_path = f"{final_path}/{script_name}_description.txt"

            if database.exists(output_video_path):
                if not database.exists(output_text_path):
                    build_infos(channel_id, title_id, title, script_name, final_path)
                continue
        
            narration_audio = AudioFileClip(audio_path)
            background_music = generate.music(audio_duration=narration_audio.duration ,mood=music_mood)
            subtitles_filename = f"{script_name}_subtitles"
            subtitles_srt = generate.subtitles(audio_path, channel_id, title_id, shorts_path, shorts=True, file_name=subtitles_filename)
            subtitles_with_expressions = generate.expressions(channel_id, title_id, shorts_path, file_name=f"{script_name}_expressions", shorts=True, subtitles_filename=subtitles_filename)
            subtitles = video_build.fix_subtitles_time(subtitles_with_expressions)

            background_video_composite = background_video.run(narration_audio.duration, video_orientation='vertical', target_resolution=(1080, 1920))
            expressions_path = f"assets/expressions/{channel_id}/chroma"
            expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration, position_h='center', position_v='center', expressions_size=1.9)

            try:
                audio = video_build.create_audio(narration_audio, background_music)
                subtitles_h = 10 if subtitles_top else 1.5
                subtitles_w = 100
                database.export('subtitles_srt', subtitles_srt)
                video = video_build.create_video(background_video_composite, expressions_images_composite, subtitles_srt, subtitles_padding=0.98, subtitles_denominators=(subtitles_w, subtitles_h))
                video_build.render_video(audio, video, output_video_path)
                build_infos(channel_id, title_id, title, script_name, final_path)
            finally:
                print("\t- Cleaning up memory before next iteration...")
                collected_objects = gc.collect()
                print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
                print("-" * 40)


def run(channel_id):
    print("--- Building Shorts ---\n")
    channel = database.get_channel_by_id(channel_id)

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    for title_id, title in enumerate(titles):
        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        shorts_path = f"storage/shorts/{channel_id}/{title_id}/"
    
        variables = prompt_variables(channel_id, title_id, title)
        shorts_ideas = ideas.run(shorts_path, variables)
        
        print("\t\t- Generating Shorts Scripts...")
        shorts_scripts = []
        for idea in shorts_ideas:
            variables['SHORTS_IDEA_JSON'] = idea
            script = generate_script.run(shorts_path, variables)
            shorts_scripts.append(script)

        print("\t\t- Done!")
        