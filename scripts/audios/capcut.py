import pyautogui as gui
import pyperclip
import time
from scripts.audios.browsing import goto_page, goto_top_of_page, open_browser
from scripts.utils import get_last_downloaded_file
import shutil
from pathlib import Path
from typing import Optional

def select_voice():
    favorites_button = (1200, 510)
    gui.click(favorites_button)
    time.sleep(1)
    
    voice_1 = (1180, 570) # +200 / +75
    gui.click(voice_1)
    time.sleep(1)

def fill_text(text):
    goto_top_of_page()
    text_box = (700, 400)
    gui.click(text_box)
    time.sleep(0.5)
    gui.click(text_box)
    time.sleep(0.5)
    gui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyperclip.copy(text)
    time.sleep(0.5)
    gui.hotkey('ctrl', 'v')
    time.sleep(1)
    
    
def generate():
    generate_button = (1450, 1020)
    gui.click(generate_button)


    
def save_audio_downloaded(file_name: str = 'audio', path: str = 'storage/audios') -> Optional[Path]:
    try:
        last_file = get_last_downloaded_file()
        file_name = file_name + '.mp3'

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
    left_click = (1590, 400)
    gui.doubleClick(left_click)
    time.sleep(0.5)
    download_button = (1620, 400)
    gui.click(download_button)
    time.sleep(0.5)
    only_audio_button = (1660, 477)
    gui.click(only_audio_button)
    time.sleep(0.5)


def run(text):
    last_file_before_download = get_last_downloaded_file()
    last_file = get_last_downloaded_file()
    fill_text(text)
    generate()
    while last_file_before_download == last_file:
        download_audio()
        time.sleep(10)
        last_file = get_last_downloaded_file()

    return last_file

           
# def run(texts):
#     select_voice()    
#     audios_paths = []
#     for i, text in enumerate(texts):
#         fill_text(text)    
#         generate()
#         download_audio()
#         time.sleep(15)
#         audios_paths.append(save_audio_downloaded(f"audio{i+1}"))
#         time.sleep(1)
    
#     return audios_paths