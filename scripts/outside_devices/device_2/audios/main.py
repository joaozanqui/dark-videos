import scripts.outside_devices.device_2.audios.capcut as capcut
from scripts.audios.utils import copy_audio_to_right_path, divide_text
import scripts.database as database

def create_srt_from_file(full_script, final_path, output_file = 'full_script'):
    blocks = divide_text(full_script, max_chars=500, separate_character=['.', '?', '\n', '!', ':'])    

    try:
        srt_content = []
        for i, block in enumerate(blocks):
            start_time_seconds = i * 60
            end_time_seconds = (i + 1) * 60
            
            start_time_ms = start_time_seconds * 1000
            end_time_ms = end_time_seconds * 1000
            
            start_time = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                start_time_seconds // 3600,
                (start_time_seconds % 3600) // 60,
                start_time_seconds % 60,
                start_time_ms % 1000
            )
            
            end_time = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                end_time_seconds // 3600,
                (end_time_seconds % 3600) // 60,
                end_time_seconds % 60,
                end_time_ms % 1000
            )

            srt_content.append(str(i + 1))
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(block.replace("\n", " ").strip())
            srt_content.append("")
        final_srt_string = "\n".join(srt_content)
        
        database.export(output_file, final_srt_string, format='srt', path=final_path)
        
        return f"{output_file}.srt"
    except Exception as e:
        print(f"Error exporting srt file: {e}")
        return ""
    
def shorts(video_id, final_path, channel):
    all_shorts = database.get_data('shorts', video_id, column_to_compare='video_id')
    all_shorts.sort(key=lambda s: s["number"])
    generating = False
    
    for shorts in all_shorts:
        if shorts['has_audio']:
            continue
        generating = True

        print(f"\t\t-{shorts['number']}...")
        srt_file = create_srt_from_file(shorts['full_script'], final_path, output_file=f"shorts_{shorts['number']}")
        shorts_name = f"shorts_{shorts['number']}"
        downloaded_file_name = f"shorts_{channel['id']}_{video_id}_{shorts['number']}"
        audio_file = capcut.run(final_path, srt_file, channel, file_name=downloaded_file_name)
        audio_path = copy_audio_to_right_path(shorts_name, final_path, audio_file)

        if not audio_path:
            print("Error coping audio...")
            return False
        
        database.update('shorts', shorts['id'], 'has_audio', True)

    if generating:
        print(f"\t\t- Shorts Finished!")
    
    return True


def download_audios(full_script, final_path, channel):
    srt_file = create_srt_from_file(full_script, final_path)
    print(f"\t\t-Generating Audio...")
    downloaded_file_name = f"full_script_{channel['id']}"
    audio_file = capcut.run(final_path, srt_file, channel, file_name=downloaded_file_name)
    audio_path = copy_audio_to_right_path(f"audio", final_path, audio_file)
        
    if not audio_path:
        print("Error coping audio...")
        return None
        
    return audio_path
