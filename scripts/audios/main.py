import importlib
import scripts.database as database
import config.keys as keys
from typing import  Optional
from pathlib import Path

def run(channel_id) -> Optional[Path]:
    # https://www.capcut.com/magic-tools/text-to-speech
    channel = database.get_item('channels', channel_id)
    titles = database.channel_titles(channel_id)
    device_id = keys.DEVICE
    audios_module_path = f"scripts.outside_devices.device_{device_id}.audios.main"
    audios = importlib.import_module(audios_module_path)

    print(f"Channel: '{channel['name']}'")
    for title in titles:        
        try:
            video = database.get_item('videos', title['id'], column_to_compare='title_id')
            final_path = f"storage/{channel['id']}/{title['title_number']}"    

            if video['has_audio']:
                audios.shorts(video['id'], final_path, channel)
                continue
            
            print(f"\t-Video {title['title_number']}")
            audio_path = audios.download_audios(video['full_script'], final_path, channel)

            database.update('videos', video['id'], 'has_audio', True)
            
            audios.shorts(video['id'], final_path, channel)

            print(f"Successful!: {audio_path}\n\n")
        except Exception as e:
            print(f"Error {channel['id']}/{title['title_number']}: {e}")
