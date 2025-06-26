# import scripts.audios.browsing as browsing
import scripts.audios.capcut as capcut
from scripts.utils import get_last_downloaded_file
import pyperclip
from typing import List, Optional
from pydub import AudioSegment
from pathlib import Path
import json
import os
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
    audio_final.export(f"{final_path}/{file_name}", format="mp3")
    
    return final_path

def run() -> Optional[Path]:
    # https://www.capcut.com/magic-tools/text-to-speech
    automatic_download = True
    path = Path("storage/thought")
    channels_path = "storage/ideas/channels.json"

    with open(channels_path, "r", encoding="utf-8") as file:
        channels = json.load(file)

    if not path.is_dir():
        print(f"Error: No video generated.")
        return

    for channel in sorted(path.iterdir(), key=lambda p: int(p.name)):
        if channel.is_dir():
            print(f"Channel: '{channels[int(channel.name)]['name']}'")
            for video in sorted(channel.iterdir(), key=lambda p: int(p.name)):              
                if video.is_dir():
                    try:
                        final_path = f"storage/audios/{channel.name}/{video.name}"
                        os.makedirs(final_path, exist_ok=True)

                        audio_files = [
                            f for f in Path(final_path).iterdir()
                        ]

                        if audio_files:
                            continue

                        script_file_path = video / "full_script.txt"
                        full_script = script_file_path.read_text(encoding="utf-8").strip()
                        texts = divide_text(full_script)
                        texts_qty = len(texts)
                        audios_paths = []
                        for i, text in enumerate(texts):
                            # print(f"({i+1}/{texts_qty}) - {channel.name}/{video.name}:\n\n{text}\n\n")
                            print(f"({i+1}/{texts_qty}) - {channel.name}/{video.name}")
                            if automatic_download:
                                audio_file = capcut.run(text)
                            else:
                                pyperclip.copy(text)
                                input("--> Copy the text, generate the audio and save it at 'Downloads' folder.\n--> Press 'Enter' when the audio is in 'Downloads' dir")
                                audio_file = get_last_downloaded_file()
                                
                            audio = copy_audio_to_right_path(f"{i+1}", final_path, audio_file)
                            if not audio:
                                print("Error coping audio...")
                                return None
                            
                            audios_paths.append(audio)
                        audio_path = merge_audio(audios_paths, final_path)
                        print(f"Successful!: {audio_path}\n\n")
                    except Exception as e:
                        print(f"Error {channel.name}/{video.name}: {e}")
    
    
    # capcut_generate_audio_page = 'https://www.capcut.com/magic-tools/text-to-speech'
    # texts = divide_text(full_text)
    # browsing.open_browser(browser='Google Chrome', system='ubuntu')
    # browsing.goto_page(capcut_generate_audio_page)
    # audios_paths = capcut.run(texts)
    # audio_path = merge_audio(audios_paths)
        
    return audio_path