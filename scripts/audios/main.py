import scripts.database as database
import scripts.audios.capcut as capcut
import pyperclip
from typing import List, Optional
import scripts.utils.device as device
from pydub import AudioSegment
from pathlib import Path
import shutil

def copy_audio_to_right_path(file_name: str, path: str, audio_file: Path) -> Optional[Path]:
    try:
        file_name = file_name + '.mp3'

        full_path = Path.cwd() / path
        full_path.mkdir(parents=True, exist_ok=True)
        file_path = full_path / file_name
        
        shutil.copy2(audio_file, file_path)

        return file_path

    except PermissionError:
        print("\nErro de Permissão: O script não tem permissão para ler a pasta de downloads ou escrever na pasta de destino.")
        return None
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        return None

def divide_text(full_text: str, max_chars: int = 10000) -> List[str]:
    paragraphs = [p for p in full_text.split('\n') if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if not current_chunk:
            current_chunk = paragraph

        elif len(current_chunk) + len(paragraph) + 1 <= max_chars:
            current_chunk += '\n' + paragraph
        else:
            chunks.append(current_chunk)
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

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

def download_audios(full_script, final_path):
    automatic_download = True
    
    texts = divide_text(full_script)
    texts_qty = len(texts)
    audios_paths = []
    for i, text in enumerate(texts):
        print(f"\t\t-Audio {i+1}/{texts_qty}")
        if automatic_download:
            audio_file = capcut.run(text)
        else:
            pyperclip.copy(text)
            input("--> Copy the text, generate the audio and save it at 'Downloads' folder.\n--> Press 'Enter' when the audio is in 'Downloads' dir")
            audio_file = device.get_last_downloaded_file()
        
        audio = copy_audio_to_right_path(f"{i+1}", final_path, audio_file)
        if not audio:
            print("Error coping audio...")
            return None
        
        audios_paths.append(audio)
    
    audio_path = merge_audio(audios_paths, final_path)
    return audio_path

def run(channel_id) -> Optional[Path]:
    # https://www.capcut.com/magic-tools/text-to-speech
    channel = database.get_item('channels', channel_id)
    titles = database.channel_titles(channel_id)

    print(f"Channel: '{channel['name']}'")
    for title in titles:        
        try:
            video = database.get_item('videos', title['id'], column_to_compare='title_id')
            if video['has_audio']:
                continue
            
            final_path = f"storage/{channel['id']}/{title['title_number']}"    
            print(f"\t-Video {title['title_number']}")
            audio_path = download_audios(video['full_script'], final_path)
            
            database.update('videos', video['id'], 'has_audio', True)
            print(f"Successful!: {audio_path}\n\n")
        except Exception as e:
            print(f"Error {channel['id']}/{title['title_number']}: {e}")

    
    # capcut_generate_audio_page = 'https://www.capcut.com/magic-tools/text-to-speech'
    # texts = divide_text(full_text)
    # browsing.open_browser(browser='Google Chrome', system='ubuntu')
    # browsing.goto_page(capcut_generate_audio_page)
    # audios_paths = capcut.run(texts)
    # audio_path = merge_audio(audios_paths)
