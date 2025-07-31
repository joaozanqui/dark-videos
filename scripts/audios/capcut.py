import pyautogui as gui
import pyperclip
import time
from scripts.audios.browsing import goto_page, goto_top_of_page, open_browser
from scripts.utils import get_last_downloaded_file
import shutil
from pathlib import Path
from typing import Optional

screen_x, screen_y = gui.size()

if screen_x > 1920:
    BUTTONS = {
        "text_box": (700, 400),
        "generate_button": (1450, 1020),
        "download_button": (1620, 400),
        "only_audio_button": (1660, 477),
    }
else:
    BUTTONS = {
        "text_box": (700, 400),
        "generate_button": (1450, 1020),
        "download_button": (1620, 430),
        "only_audio_button": (1625, 510),
    }

def fill_text(text):
    goto_top_of_page()
    gui.click(BUTTONS['text_box'])
    time.sleep(0.5)
    gui.click(BUTTONS['text_box'])
    time.sleep(0.5)
    gui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyperclip.copy(text)
    time.sleep(0.5)
    gui.hotkey('ctrl', 'v')
    time.sleep(1)
    
def generate():
    gui.click(BUTTONS['generate_button'])

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
    time.sleep(2)
    gui.click(BUTTONS['download_button'])
    time.sleep(0.5)
    gui.click(BUTTONS['only_audio_button'])
    time.sleep(0.5)


def run(text):
    last_file_before_download = get_last_downloaded_file()
    last_file = get_last_downloaded_file()
    fill_text(text)
    generate()
    while last_file_before_download == last_file:
        download_audio()
        time.sleep(10)
        gui.hotkey('enter')
        time.sleep(1)
        last_file = get_last_downloaded_file()

    return last_file
