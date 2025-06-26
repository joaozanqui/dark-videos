import os
from pathlib import Path
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import json
from scripts.utils import ALLOWED_EXTENSIONS
import scripts.video_build.generate as generate

def create_subtitles(subtitles_path, background_image):
    def subtitle_generator(txt):
        return TextClip(
            txt,
            font='assets/font.ttf',
            fontsize=48,
            color='white',
            stroke_color='#000000',
            stroke_width=1.5,
            method='caption',
            align='center',
            size=(background_image.w * 0.8, None),
            bg_color='rgba(0, 0, 0, 0.6)'
        )
    
    subtitles = SubtitlesClip(subtitles_path, subtitle_generator)
    subtitles = subtitles.set_position(lambda t: ('center', background_image.h/2))
    
    return subtitles


def create_video(image_path: str, narration_audio: AudioFileClip, music_audio: AudioFileClip, subtitles_path: str, output_path: str):    
    audio = CompositeAudioClip([narration_audio, music_audio])
    background_image = ImageClip(image_path).set_duration(narration_audio.duration)
    subtitles = create_subtitles(subtitles_path, background_image) 
    
    final_video = CompositeVideoClip([background_image, subtitles])
    
    final_video.audio = audio
    final_video.fps = 24
    
    print(f"\t\t-Exporting final video: {output_path}")
    final_video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='audio.m4a',
        remove_temp=True,
        logger=None
    )
    
    print("\t\t-Video built successful!")

def run():
    print("--- Building Videos ---\n")
    music_mood = "calm"

    with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
        channels = json.load(file)    

    for i, channel in enumerate(channels):
        print(f"- {channel['name']}")
        with open(f"storage/ideas/titles/{i}.json", "r", encoding="utf-8") as file:
            titles = json.load(file)

        for j, title in enumerate(titles):
            print(f"\t- {title['title']}")
            description_file = f"storage/thought/{i}/{j}/description.txt"
            audio_path = f"storage/audios/{i}/{j}/audio.mp3"
            image_path = f"storage/images/{i}/{j}"
            
            has_description = os.path.exists(description_file)
            has_audio = os.path.exists(audio_path)
            
            for ext in ALLOWED_EXTENSIONS:
                has_image = os.path.exists(f"{image_path}/image.{ext}")
                if has_image:
                    image_path = f"{image_path}/image.{ext}"
                    break
            
            if not has_image or not has_audio or not has_description:
                continue

            narration_audio = AudioFileClip(audio_path)
            music_audio = generate.music(audio_duration=narration_audio.duration ,mood=music_mood)
            subtitles_path = generate.subtitles(audio_path, output_path=f"storage/subtitles/{i}/{j}")

            final_path = "storage/videos"
            video_path = f"{final_path}/{i}/{j}"
            os.makedirs(video_path, exist_ok=True)
            output_dir = Path(video_path)
            os.makedirs(output_dir, exist_ok=True)
            output_video_path = str(output_dir / f"video.mp4")
            create_video(image_path, narration_audio, music_audio, subtitles_path, output_video_path)

            thumbnail_path = f"storage/thumbnails/{i}/{j}"
            thumbnail_dir = Path(thumbnail_path)
            os.makedirs(thumbnail_dir, exist_ok=True)
            output_thumbnail_path = str(thumbnail_dir / f"image.png")
            generate.thumbnail(image_path, title['title'], output_thumbnail_path)
    
    print("\n--- Process Finished ---")
