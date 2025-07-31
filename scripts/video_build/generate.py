import whisper
import re
import json
from scripts.utils import get_language_code, get_prompt, analyze_with_gemini, format_json_response, get_allowed_expressions
import scripts.database as database
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips
import random

def expressions(channel_id, title_id):
    output_path = f"storage/thought/{channel_id}/{title_id}"
    expressions_file = f"{output_path}/expressions.json"
    
    if os.path.exists(expressions_file):
        return database.get_expressions(channel_id, title_id)
    
    print("\t\t-Taking expressions...")
    subtitles_srt = database.get_subtitles(channel_id, title_id)

    pattern = re.compile(
        r'(\d+)\s*\n'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s-->\s'
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*\n'
        r'(.*?)(?=\n{2,}|\Z)',
        re.DOTALL
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

    allowed_expressions = get_allowed_expressions(channel_id, is_video=True)
    variables = {
        "ALLOWED_EXPRESSIONS": allowed_expressions
    }

    all_expressions = []
    max_expressions_per_run = 100
    subtitles_qty = len(subtitles_json)
    try:
        for i in range(0, subtitles_qty, max_expressions_per_run):
            bigest_id = i + max_expressions_per_run
            batch = subtitles_json[i:bigest_id]
            variables['DATA'] = batch
            prompt = get_prompt('build', 'expressions', variables)
            prompt_json = json.loads(prompt)

            response = analyze_with_gemini(prompt_json=prompt_json)
            all_expressions.extend(format_json_response(response))
            print(f"\t\t\t{bigest_id if bigest_id < subtitles_qty else subtitles_qty}/{subtitles_qty}")
    except Exception as e:
        print(f"\t\t\tError taking expressions: {e}")
        print(f"\t\t\tTrying again...")
        return expressions(channel_id, title_id)
    
    for expression in all_expressions:
        subtitles_json[expression['id']-1]['expression'] = expression['expression']

    database.export('expressions', subtitles_json, 'json', f"{output_path}/")
    return subtitles_json

def subtitles(audio_path, channel_id, title_id):   
    subtitles_path = f"storage/thought/{channel_id}/{title_id}"
    subtitles_file = f"{subtitles_path}/subtitles.srt"
    
    if os.path.exists(subtitles_file):
        return database.get_subtitles(channel_id, title_id)
    
    channel = database.get_channel_by_id(channel_id)
    language = channel['language']
    print("\t\t-Generating subtitles...")

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
        database.export('subtitles', result["segments"], format='srt', path=f"{subtitles_path}/")
        return database.get_subtitles(channel_id, title_id)
    
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
