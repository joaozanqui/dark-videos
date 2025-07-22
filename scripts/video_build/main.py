import os
from pathlib import Path
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import json
from scripts.utils import ALLOWED_IMAGES_EXTENSIONS
import scripts.video_build.generate as generate
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
import shutil

def create_audio(narration_audio: AudioFileClip, background_music: AudioFileClip, intro_file: str):
    main_audio = CompositeAudioClip([narration_audio, background_music])

    if os.path.exists(intro_file):
        intro_audio = AudioFileClip(intro_file)
        final_audio = concatenate_audioclips([intro_audio, main_audio])
    else:
        final_audio = main_audio

    return final_audio

def create_subtitles(subtitles_path, background_video_composite):
    def subtitle_generator(txt):
        return TextClip(
            txt,
            font='assets/font.ttf',
            fontsize=64,
            color='yellow',
            method='caption',
            align='center',
            size=(int(background_video_composite.w * 0.45), None),
            bg_color='rgba(0, 0, 0, 0.6)',
        )

    subtitles = SubtitlesClip(subtitles_path, subtitle_generator)
    subtitles_x = int(background_video_composite.w // 2)
    subtitles_y = int(background_video_composite.h // 2.5)
    subtitles = subtitles.set_position((subtitles_x, subtitles_y))
    subtitles = subtitles.set_duration(background_video_composite.duration)
    return subtitles


def create_video(
    background_video_composite: CompositeVideoClip,
    subtitles_path: str,
    expressions_images_composite: CompositeVideoClip,
    intro_file: str,
):
    subtitles = create_subtitles(subtitles_path, background_video_composite)
    main_video = CompositeVideoClip([
        background_video_composite,
        expressions_images_composite,
        subtitles
    ])

    if os.path.exists(intro_file):
        intro_clip = VideoFileClip(intro_file)
        final_video = concatenate_videoclips([intro_clip, main_video])
    else:
        final_video = main_video

    return final_video

def render_video(audio, video, output_path):       
    video.audio = audio
    video.fps = 24
    
    print(f"\t\t-Exporting final video: {output_path}")
    video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='audio.m4a',
        remove_temp=True,
    )
    
    print("\t\t-Video built successful!")

def save_infos(title, description_file, output_path):
    try:
        print("\t\t-Saving infos...")
        with open(description_file, "r", encoding="utf-8") as file:
            description = file.read()

        infos = f"{title}\n\n{description}"
        with open(output_path, "w", encoding="utf-8") as infos_path:
                infos_path.write(infos)
        print("\t\t-Done!")
        
    except Exception as e:
        print(f"\t\t-Error saving infos: {e}")

    return    

def fix_subtitles_time(subtitles):
    last_end = '00:00:00,000'
    for subtitle in subtitles:
        subtitle['start'] = last_end
        last_end = subtitle['end']
    
    return subtitles

def run(channel_id):
    print("--- Building Videos ---\n")
    music_mood = "calm"

    with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
        channels = json.load(file)    

    channel = channels[int(channel_id)-1]

    print(f"- {channel['name']}")
    with open(f"storage/ideas/titles/{channel_id}.json", "r", encoding="utf-8") as file:
        titles = json.load(file)

    for title_id, title in enumerate(titles):
        print(f"\t-({channel_id}/{title_id}) {title['title']}")
        final_path = f"storage/videos/{channel_id}/{title_id}"
        os.makedirs(final_path, exist_ok=True)
        final_dir = Path(final_path)
        output_video_path = str(final_dir / f"video.mp4")
        if os.path.exists(output_video_path):
            continue

        default_path = f"storage/thought/{channel_id}/{title_id}"
        description_file = f"{default_path}/description.txt"
        audio_path = f"{default_path}/audio.mp3"
        image_path = ''
        
        has_description = os.path.exists(description_file)
        has_audio = os.path.exists(audio_path)
        
        if not has_audio or not has_description:
            continue

        narration_audio = AudioFileClip(audio_path)
        background_music = generate.music(audio_duration=narration_audio.duration ,mood=music_mood)
        subtitles_path = generate.subtitles(audio_path, output_path=default_path)
        subtitles_with_expressions = generate.expressions(subtitles_path, output_path=default_path)
        subtitles = fix_subtitles_time(subtitles_with_expressions)

        background_video_composite = background_video.run(narration_audio.duration, output_path=default_path)
        expressions_path = f"assets/expressions/{channel_id}"
        expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration)
        intro_file = f"assets/intros/{channel_id}/intro.mp4"

        # ver o que fazer com a imagem -------------------------------------------------------------------
        # for ext in ALLOWED_IMAGES_EXTENSIONS:
        #     has_image = os.path.exists(f"{default_path}/image.{ext}")
        #     if has_image:
        #         image_path = f"{default_path}/image.{ext}"
        #         break

        # if not has_image:
        #     continue 
        audio = create_audio(narration_audio, background_music, intro_file)
        video = create_video(background_video_composite, subtitles_path, expressions_images_composite, intro_file)
        render_video(audio, video, output_video_path)
        
        output_thumbnail_path = str(final_dir / f"thumbnail.png")
        # generate.thumbnail(image_path, title['title'], output_thumbnail_path)
        if os.path.exists(image_path):
            shutil.copy2(image_path, output_thumbnail_path)

        output_infos_path = str(final_dir / f"infos.txt")
        save_infos(title['title'], description_file, output_infos_path)
    
    print("\n--- Process Finished ---")
