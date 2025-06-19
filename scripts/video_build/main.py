import os
from pathlib import Path
import whisper
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import json
import random
from typing import Optional
import yt_dlp

def get_music(music_type: str) -> str:
    musics_path = Path("musics.json")
    output_dir = Path("storage/audios")

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(musics_path, "r", encoding="utf-8") as file:
            all_music_data = json.load(file)

        available_musics = [
            url
            for group in all_music_data
            if group.get("type") == music_type
            for url in group.get("musics", [])
        ]

        if not available_musics:
            return None

        chosen_music_url = random.choice(available_musics)

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"music chosen error - 'musics.json': {e}")
        return None


    try:
        output_path = output_dir / "background_music"
        format = "mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path),
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([chosen_music_url])

        print(f"music chosen: {output_path}")
        return f"{str(output_path)}.{format}"

    except Exception as e:
        print(f"Error chosen music: {e}")
        return None

def get_image() -> Optional[str]:
    try:
        image_dir = Path("input/image/")

        if not image_dir.is_dir():
            print(f"Erro: Dir '{image_dir}' not found.")
            return None

        allowed_extensions = {".png", ".jpg", ".jpeg"}
        image_files = [
            file
            for file in image_dir.iterdir()
            if file.is_file() and file.suffix.lower() in allowed_extensions
        ]

        if not image_files:
            print(f"Image not found at '{image_dir}'.")
            return None

        chosen_image = random.choice(image_files)

        print(f"Image found!")

        return str(chosen_image)

    except Exception as e:
        print(f"Ocorreu um erro inesperado ao tentar obter a imagem: {e}")
        return None


def generate_subtitles(audio_path: str, language: str) -> str:
    print("Generating subtitles...")
    
    subtitles_dir = Path("storage/subtitles")
    subtitles_dir.mkdir(exist_ok=True)
    subtitles_path = subtitles_dir / f"{Path(audio_path).stem}.srt"
    model = whisper.load_model("medium")
    
    try:
        result = model.transcribe(
                    audio_path,
                    language=language,
                    # beam_size=3,
                    # best_of=3, 
                    # fp16=False  
                    verbose=False
                )   

        with open(subtitles_path, "w", encoding="utf-8") as subtitles_file:
            for i, segment in enumerate(result["segments"]):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()

                start_subtitiles = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02},{int(start_time%1*1000):03}"
                end_subtitles = f"{int(end_time//3600):02}:{int(end_time%3600//60):02}:{int(end_time%60):02},{int(end_time%1*1000):03}"

                subtitles_file.write(f"{i + 1}\n")
                subtitles_file.write(f"{start_subtitiles} --> {end_subtitles}\n")
                subtitles_file.write(f"{text}\n\n")

        print(f"Subtitles generated successfull: {subtitles_path}")
        return str(subtitles_path)
    
    except Exception as e:
        print(f"Subtitles error: {e}")
        return None
    finally:
        del model


def create_video(image_path: str, audio_path: str, music_path: str, subtitles_path: str, output_path: str):
    narration_audio = AudioFileClip(audio_path)
    music_audio = AudioFileClip(music_path).volumex(0.1) 
    final_music = music_audio.set_duration(narration_audio.duration)
    final_audio = CompositeAudioClip([narration_audio, final_music])
    
    background_image = ImageClip(image_path).set_duration(narration_audio.duration)
    
    def subtitle_generator(txt):
        return TextClip(
            txt,
            font='Montserrat-Bold',
            fontsize=48,
            color='white',
            stroke_color='#000000',
            stroke_width=2.5,
            method='caption',
            align='center',
            size=(background_image.w * 0.8, None),
            bg_color='rgba(0, 0, 0, 0.6)'
        )
    
    subtitles = SubtitlesClip(subtitles_path, subtitle_generator)
    
    subtitles = subtitles.set_position(lambda t: ('center', background_image.h - 150))
    
    final_video = CompositeVideoClip([background_image, subtitles])
    
    final_video.audio = final_audio
    final_video.fps = 24
    
    print(f"Exportando o vídeo final: {output_path}")
    final_video.write_videofile(
        output_path, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        logger='bar'
    )
    
    print("Vídeo construído com sucesso!")



def run(audio_path: str, language: str, music_type: str):
    print("--- Building Video ---")
    audio_filename = audio_path.split('/')[-1].split('.')[0]

    music_path = get_music(music_type)
    image_path = get_image()

    subtitles_file = f"storage/subtitles/{audio_filename}.srt"
    subtitles_path = subtitles_file if os.path.exists(subtitles_file) else generate_subtitles(audio_path, language)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_video_path = str(output_dir / f"{Path(audio_path).stem}_final_video.mp4")

    create_video(image_path, audio_path, music_path, subtitles_path, output_video_path)
    
    print("\n--- Process Finished ---")
