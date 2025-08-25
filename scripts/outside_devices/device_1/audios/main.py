import scripts.outside_devices.device_1.audios.capcut as capcut
from pathlib import Path
import scripts.database as database
from pydub import AudioSegment
from scripts.audios.utils import copy_audio_to_right_path, divide_text

def shorts(video_id, final_path):
    print(f"\t\t-Shorts:")
    all_shorts = database.get_data('shorts', video_id, column_to_compare='video_id')
    generating = False

    for shorts in all_shorts:
        if shorts['has_audio']:
            continue
        generating = True

        print(f"\t\t-{shorts['number']}...")
        audio_file = capcut.run(shorts['full_script'])
        shorts_name = f"shorts_{shorts['number']}"
        audio_path = copy_audio_to_right_path(shorts_name, final_path, audio_file)

        if not audio_path:
            print("Error coping audio...")
            return False
        
        database.update('shorts', shorts['id'], 'has_audio', True)

    if generating:
        print(f"\t\t- Shorts Finished!")

    print(f"\t\t- Shorts Finished!: {audio_path}")
    return True

def merge_audio(audios_paths, final_path):
    audio_final = AudioSegment.empty()

    for path in audios_paths:
        audio = AudioSegment.from_file(path)
        audio_final += audio 

    file_name = "audio.mp3"
    output_path = Path(final_path) / file_name
    audio_final.export(output_path, format="mp3")

    
    for path in audios_paths:
        Path(path).unlink()

    return str(output_path)

def download_audios(full_script, final_path, channel):
    texts = divide_text(full_script)
    texts_qty = len(texts)
    audios_paths = []
    for i, text in enumerate(texts):
        print(f"\t\t-Audio {i+1}/{texts_qty}")
        audio_file = capcut.run(text)
        audio = copy_audio_to_right_path(f"{i+1}", final_path, audio_file)
        
        if not audio:
            print("Error coping audio...")
            return None
        
        audios_paths.append(audio)
    
    audio_path = merge_audio(audios_paths, final_path)
    return audio_path
