import pyautogui as gui
import pyperclip
import time
from audios.browsing import goto_bottom_of_page, goto_top_of_page
import os
import shutil
from pathlib import Path
from typing import Optional

def select_voice():
    favorites_button = (1310, 540)
    gui.click(favorites_button)
    time.sleep(1)
    
    voice_1 = (1300, 600) # +200 / +75
    gui.click(voice_1)
    time.sleep(1)

def fill_text(text):
    goto_top_of_page()
    text_box = (700, 400)
    gui.click(text_box)
    gui.hotkey('ctrl', 'a')
    pyperclip.copy(text)
    gui.hotkey('ctrl', 'v')
    time.sleep(1)
    
    
def generate():
    generate_button = (1500, 960)
    gui.click(generate_button)
    time.sleep(120)
    
def save_audio_downloaded(file_name: str = 'audio', path: str = 'storage/audios') -> Optional[Path]:
    try:
        file_name = file_name + '.mp3'
        downloads_path = Path.home() / 'Downloads'
        
        if not downloads_path.exists() or not downloads_path.is_dir():
            downloads_path = Path.home() / 'Transferências'
            if not downloads_path.exists() or not downloads_path.is_dir():
                return None
       
        arquivos = [f for f in downloads_path.iterdir() if f.is_file() and not str(f).endswith(('.tmp', '.crdownload'))]

        if not arquivos:
            return None

        last_file = max(arquivos, key=os.path.getctime)
        full_path = Path.cwd() / path
        full_path.mkdir(parents=True, exist_ok=True)
        file_path = full_path / file_name
        
        shutil.copy2(last_file, file_path)

        return file_path

    except PermissionError:
        print("\nErro de Permissão: O script não tem permissão para ler a pasta de downloads ou escrever na pasta de destino.")
        return None
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        return None
    
def download_audio():
    download_button = (1700, 430)
    gui.click(download_button)
    time.sleep(1)
    only_audio_button = (1700, 490)
    gui.click(only_audio_button)
           
def run(texts):
    select_voice()    
    audios_paths = []
    for i, text in enumerate(texts):
        fill_text(text)    
        generate()
        download_audio()
        time.sleep(15)
        audios_paths.append(save_audio_downloaded(f"audio{i+1}"))
        time.sleep(1)
    
    return audios_paths