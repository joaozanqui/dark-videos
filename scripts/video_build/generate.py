import whisper
from scripts.storytelling.utils import build_template
import re
from pathlib import Path
import json
from scripts.utils import get_final_language, get_language_code, export, get_prompt, analyze_with_gemini, format_json_response
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips
import random

def expressions(subtitles_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    expressions_file = f"{output_path}/expressions.json"
    
    if os.path.exists(expressions_file):
        with open(expressions_file, "r", encoding="utf-8") as file:
            all_expressions = json.load(file)
        
        return all_expressions 
    
    print("\t\t-Taking expressions...")
    with open(subtitles_path, "r", encoding="utf-8") as file:
        subtitles_srt = file.read()
    pattern = re.compile(
        r"(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s-->\s"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s*\n"
        r"((?:.+\n?)+?)"
        r"(?=\n\d+\n|\s*\Z)"
    )

    subtitles_json = []
    for match in pattern.finditer(subtitles_srt):
        id = int(match.group(1))
        start = match.group(2)
        end = match.group(3)
        text = match.group(4).strip().replace('\n', ' ')
        
        subtitles_json.append({
            "id": id,
            "start": start,
            "end": end,
            "text": text.replace("'", "")
        })

    default_prompt_path = 'default_prompts/build/expressions.json'
    
    all_expressions = []
    max_expressions_per_run = 100
    subtitles_qty = len(subtitles_json)
    try:
        for i in range(0, subtitles_qty, max_expressions_per_run):
            bigest_id = i + max_expressions_per_run
            batch = subtitles_json[i:bigest_id]
            prompt = get_prompt(default_prompt_path, {"DATA": batch})
            prompt_json = json.loads(prompt)

            response = analyze_with_gemini(prompt_json=prompt_json)
            all_expressions.extend(format_json_response(response))
            print(f"\t\t\t{bigest_id if bigest_id < subtitles_qty else subtitles_qty}/{subtitles_qty}")
    except Exception as e:
        print(f"\t\t\tError taking expressions: {e}")
        print(f"\t\t\tTrying again...")
        return expressions(subtitles_path, output_path)
    
    for expression in all_expressions:
        subtitles_json[expression['id']-1]['expression'] = expression['expression']

    export('expressions', subtitles_json, 'json', f"{output_path}/")
    return subtitles_json

def subtitles(audio_path, output_path):   
    os.makedirs(output_path, exist_ok=True)
    subtitles_file = f"{output_path}/subtitles.srt"
    
    if os.path.exists(subtitles_file):
        return subtitles_file 
    
    language = get_final_language()
    print("\t\t-Generating subtitles...")

    subtitles_dir = Path(output_path)
    subtitles_dir.mkdir(exist_ok=True)
    subtitles_path = subtitles_dir / f"subtitles.srt"
    model = whisper.load_model("medium")
    language_code = get_language_code(language)

    try:
        result = model.transcribe(
                    audio_path,
                    language=language_code,
                    # beam_size=3,
                    # best_of=3, 
                    # fp16=False  
                    verbose=False
                )   

        with open(subtitles_path, "w", encoding="utf-8") as file:
            for i, segment in enumerate(result["segments"]):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()

                start_subtitiles = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02},{int(start_time%1*1000):03}"
                end_subtitles = f"{int(end_time//3600):02}:{int(end_time%3600//60):02}:{int(end_time%60):02},{int(end_time%1*1000):03}"

                file.write(f"{i + 1}\n")
                file.write(f"{start_subtitiles} --> {end_subtitles}\n")
                file.write(f"{text}\n\n")

        print(f"\t\t-Subtitles generated successfull: {subtitles_path}")
        return str(subtitles_path)
    
    except Exception as e:
        print(f"Subtitles error: {e}")
        return None
    finally:
        del model

def music(audio_duration, mood):  
    print(f"\t\t-Merging background music ({audio_duration}s)...")
    musics_path = f"assets/musics/{mood}"

    mp3_files = [
        os.path.join(musics_path, f)
        for f in os.listdir(musics_path)
        if f.lower().endswith(".mp3")
    ]

    if not mp3_files:
        raise Exception(f"No music in found {musics_path}")

    random.shuffle(mp3_files)

    collected_clips = []
    total_duration = 0

    for music in mp3_files:
        try:
            clip = AudioFileClip(music)
        except Exception as e:
            print(f"Error loading {music}: {e}")
            continue

        collected_clips.append(clip)
        total_duration += clip.duration

        if total_duration >= audio_duration:
            break

    if not collected_clips:
        raise Exception("No valid music loaded.")

    merged = concatenate_audioclips(collected_clips)

    if merged.duration > audio_duration:
        merged = merged.subclip(0, audio_duration)
    
    final_music = merged.volumex(0.1) 
    return final_music
