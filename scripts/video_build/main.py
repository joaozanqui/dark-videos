import os
from pathlib import Path
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import scripts.video_build.generate as generate
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
import gc
import scripts.database as database
import srt
from datetime import timedelta

def create_audio(narration_audio: AudioFileClip, background_music: AudioFileClip, intro_file: str):
    background_music = background_music.volumex(0.5)
    main_audio = CompositeAudioClip([narration_audio, background_music])

    if os.path.exists(intro_file):
        intro_audio = AudioFileClip(intro_file)
        final_audio = concatenate_audioclips([intro_audio, main_audio])
    else:
        final_audio = main_audio

    return final_audio

def create_subtitles(background_video_composite, subtitles_srt):
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
    
    parsed_subs = list(srt.parse(subtitles_srt))
    subtitles_data = [
        ((sub.start.total_seconds(), sub.end.total_seconds()), sub.content)
        for sub in parsed_subs
    ]

    subtitles = SubtitlesClip(subtitles_data, subtitle_generator)
    subtitles_x = int(background_video_composite.w // 2)
    subtitles_y = int(background_video_composite.h // 2.5)
    subtitles = subtitles.set_position((subtitles_x, subtitles_y))
    subtitles = subtitles.set_duration(background_video_composite.duration)
    return subtitles

def create_video(
    background_video_composite: CompositeVideoClip,
    expressions_images_composite: CompositeVideoClip,
    intro_file: str,
    subtitles_srt: str,
):
    subtitles = create_subtitles(background_video_composite, subtitles_srt)
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

def build_video(audio_path, default_path, output_video_path, music_mood, channel_id, title_id):
    narration_audio = AudioFileClip(audio_path)
    background_music = generate.music(audio_duration=narration_audio.duration ,mood=music_mood)
    subtitles_srt = generate.subtitles(audio_path, channel_id, title_id)
    subtitles_with_expressions = generate.expressions(channel_id, title_id)
    subtitles = fix_subtitles_time(subtitles_with_expressions)

    background_video_composite = background_video.run(narration_audio.duration, output_path=default_path)
    expressions_path = f"assets/expressions/{channel_id}/chroma"
    expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration)
    intro_file = f"assets/intros/{channel_id}/intro.mp4"

    audio = create_audio(narration_audio, background_music, intro_file)
    video = create_video(background_video_composite, expressions_images_composite, intro_file, subtitles_srt)
    render_video(audio, video, output_video_path)

def render_video(audio, video, output_path):       
    video.audio = audio
    video.fps = 24
    gc.collect()
    
    print(f"\t\t-Exporting final video: {output_path}")
    video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='audio.m4a',
        remove_temp=True,
    )
    
    print("\t\t-Video built successful!")

def save_infos(title, channel_id, title_id):
    output_path = f"storage/videos/{channel_id}/{title_id}"
    file_name = "infos"
    if os.path.exists(f"{output_path}/{file_name}.txt"):
        return
        
    try:
        print("\t\t-Saving infos...")
        description = database.get_video_description(channel_id, title_id)
        infos = f"{title}\n\n{description}"
        database.export(file_name, infos, path=f"{output_path}/")
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

def has_all_files(audio_path, description_path):
    has_description = os.path.exists(description_path)
    has_audio = os.path.exists(audio_path)
    
    if not has_audio or not has_description:
        print(f"\t\t-{'No audio file' if not has_audio else 'No description file' if not has_description else ''}")
        return False
    
    return True

def run(channel_id):
    print("--- Building Videos ---\n")
    music_mood = "calm"
    channel = database.get_channel_by_id(channel_id)

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    for title_id, title in enumerate(titles):
        print(f"\t-({channel_id}/{title_id}) {title['title']}")

        final_path = f"storage/videos/{channel_id}/{title_id}"
        os.makedirs(final_path, exist_ok=True)
        final_dir = Path(final_path)
        output_video_path = str(final_dir / f"video.mp4")
        
        is_video_generated = os.path.exists(output_video_path)
        default_path = f"storage/thought/{channel_id}/{title_id}"
        description_path = f"{default_path}/description.txt"
        audio_path = f"{default_path}/audio.mp3"
        
        if not has_all_files(audio_path, description_path):
            continue
        
        save_infos(title['title'], channel_id, title_id)

        if is_video_generated:
            print(f"\t\t-Video file already exists!")
            continue

        build_video(audio_path, default_path, output_video_path, music_mood, channel_id, title_id)

    
    print("\n--- Process Finished ---")
