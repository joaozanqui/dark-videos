import pyautogui as gui
import pyperclip
import time
import scripts.utils.device as device

screen_x, screen_y = gui.size()

if screen_x > 1920:
    BUTTONS = {
        "text_box": (300, 230),
        "generate_button": (350, 1037),
        "download_button": (875, 340),
        "free_download_button": (950, 330),
    }
else:
    BUTTONS = {
        "text_box": (300, 230),
        "generate_button": (350, 1037),
        "download_button": (875, 340),
        "free_download_button": (950, 330),
    }

def fill_text(text):
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
    time.sleep(0.5)
    gui.click(BUTTONS['generate_button'])
    time.sleep(3)

def download_image():
    time.sleep(0.5)
    gui.click(BUTTONS['download_button'])
    time.sleep(0.5)
    gui.click(BUTTONS['free_download_button'])
    time.sleep(0.5)

def run(text):
    last_file_before_download = device.get_last_downloaded_file()
    last_file = device.get_last_downloaded_file()
    time.sleep(2)
    fill_text(text)
    generate()
    

    while last_file_before_download == last_file:
        gui.hotkey('esc')
        time.sleep(1)
        gui.hotkey('esc')
        download_image()
        time.sleep(5)
        last_file = device.get_last_downloaded_file()

    return last_file