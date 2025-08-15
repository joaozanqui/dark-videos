import whisper
import scripts.database as database
import scripts.utils.handle_text as handle_text
import assets.main as assets
import scripts.utils.gemini as gemini
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips
import random

def get_batch(batch, variables):
    variables['DATA'] = batch
    prompt = database.get_prompt_template('build', 'expressions', variables)
    response = gemini.run(prompt_json=prompt)

    expressions_json = handle_text.format_json_response(response)
    if not expressions_json:
        print(f"\t\t\t\t- Trying again...")
        gemini.goto_next_model()
        return get_batch(batch, variables)
    
    return expressions_json

def expressions(subtitles, channel_id, id, table='videos'):
    print("\t\t-Taking expressions...")
    variables = {"ALLOWED_EXPRESSIONS": assets.get_allowed_expressions(channel_id, is_video=True)}

    all_expressions = []
    max_expressions_per_run = 100
    subtitles_qty = len(subtitles)
    try:
        for i in range(0, subtitles_qty, max_expressions_per_run):
            bigest_id = i + max_expressions_per_run
            batch = subtitles[i:bigest_id]
            expressions_json = get_batch(batch, variables)

            all_expressions.extend(expressions_json)
            print(f"\t\t\t{bigest_id if bigest_id < subtitles_qty else subtitles_qty}/{subtitles_qty}")
    except Exception as e:
        print(f"\t\t\tError taking expressions: {e}")
        print(f"\t\t\tTrying again...")
        return expressions(subtitles, channel_id, id)
    
    for expression in all_expressions:
        subtitles[expression['id']-1]['expression'] = expression['expression']

    return database.update(table, id, 'expressions', subtitles)

def subtitles(audio_path, language, id, table='videos'):   
    print("\t\t-Generating subtitles...")

    model = whisper.load_model("medium")
    language_code = handle_text.get_language_code(language)

    try:
        result = model.transcribe(
                    audio_path,
                    language=language_code,
                    # beam_size=3,
                    # best_of=3, 
                    # fp16=False  
                    verbose=False
                )   
        return database.update(table, id, 'subtitles', result["segments"])
    
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
