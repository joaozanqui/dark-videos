import pyautogui as gui
import time
import scripts.utils.device as device
import scripts.database as database
from scripts.outside_devices.device_2.utils import search_file, wait_process
from config.keys import DEVICE
import pyperclip
from pathlib import Path

screen_x, screen_y = gui.size()

if screen_x > 1920:
    BUTTONS = {
        "text_tab": (150, 55),
        "srt_tab": (70, 305),
        "srt_import": (455, 155),
        "add_srt": (210, 200),
        "text_to_speech_tab": (1700, 55),
        "character_tab": (1825, 100),
        "wachy_voice": (1695, 150),
        "start_reading": (1850, 550),
        "check_text": (1125, 410),
        "select_audio_right": (1880, 900),
        "select_audio_left": (125, 900),
        "export": (1750, 10),
        "check_export": (1125, 250),
        "export_confirm": (1145, 825),
        "ok": (1225, 640),
        "click_to_select": (1740, 825),
    }
else:
    VOICES_TYPE = {
        "more_voices": (1885, 100),
        "character": (1475, 130),
        "portuguese": (1710, 130),
        "male": (1785, 130),
    }
    VOICES = {
        "wacky": (1700, 215),
        "lucas": (1700, 300),
    }
    BUTTONS = {
        "text_tab": (130, 50),
        "srt_tab": (65, 305),
        "srt_import": (155, 105),
        "add_srt": (205, 190),
        "text_to_speech_tab": (1700, 55),
        "start_reading": (1850, 555),
        "check_text": (1105, 410),
        "click_to_select": (1740, 825),
        "export": (1750, 10),
        "check_export": (1125, 250),
        # "disable_video": (1010, 340),
        # "enable_audio": (1010, 620),
        "export_confirm": (1145, 825),
        "replace": (915, 600),
        "ok": (1225, 640),
    }

def export(file_name):
    gui.click(BUTTONS['export'])
    time.sleep(1)
    wait_process(BUTTONS['check_export'], time_sleep=2)
    gui.click(BUTTONS['check_export'])
    time.sleep(0.5)
    gui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyperclip.copy(file_name)
    time.sleep(0.5)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    # gui.click(BUTTONS['disable_video'])
    # time.sleep(1)
    # gui.click(BUTTONS['enable_audio'])
    # time.sleep(1)
    gui.click(BUTTONS['export_confirm'])
    time.sleep(0.5)
    gui.click(BUTTONS['replace'])
    time.sleep(0.5)

def merge_audio():
    gui.click(BUTTONS['click_to_select'])
    gui.hotkey('ctrl', 'a')
    time.sleep(0.5)

    gui.hotkey('alt', 'g')
    time.sleep(2)

def text_to_speech(voice_type, voice_name):
    gui.click(BUTTONS['click_to_select'])
    time.sleep(2)
    gui.hotkey('ctrl', 'a')
    time.sleep(1)

    gui.click(BUTTONS['text_to_speech_tab'])
    time.sleep(2)

    voice_type_button = VOICES_TYPE[voice_type]
    # if voice_type_button[1] == 130:
    #     gui.click(VOICES_TYPE["more_voices"])
    #     time.sleep(1)
    gui.click(voice_type_button)
    time.sleep(1)
    
    gui.click(VOICES[voice_name])
    time.sleep(1)

    gui.click(BUTTONS["start_reading"])
    time.sleep(0.5)
    gui.click(BUTTONS["check_text"])
    wait_process(BUTTONS["check_text"], time_sleep=2)

def select_srt(final_path, srt_file):
    gui.click(BUTTONS['text_tab'])
    time.sleep(4)
    gui.click(BUTTONS['srt_tab'])
    time.sleep(2)
    gui.click(BUTTONS['srt_import'])
    time.sleep(1)
    search_file(final_path, srt_file)
    time.sleep(2)
    gui.doubleClick(BUTTONS['add_srt'])
    time.sleep(5)

def restart():
    gui.click(BUTTONS['ok'])
    time.sleep(1)
    gui.click(BUTTONS['click_to_select'])
    time.sleep(1)
    gui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    gui.hotkey('delete')
    time.sleep(0.5)

def run(final_path, srt_file, channel, file_name='tmp_audio'):
    restart()
    device_infos = database.get_item('devices', DEVICE)
    srt_path = f"{device_infos['final_path']}/{final_path}"
    select_srt(srt_path, srt_file)
    text_to_speech(channel['capcut_voice_type'], channel['capcut_voice_name'])
    merge_audio()
    
    
    last_file_before_download = device.get_last_downloaded_file()
    export(file_name)
    last_file = device.get_last_downloaded_file()
    while last_file_before_download == last_file:
        print(last_file_before_download)
        print(last_file)
        time.sleep(1)
        last_file = device.get_last_downloaded_file()

    time.sleep(1)
    last_file_path = str(Path(last_file).with_stem(file_name))
    return last_file_path

