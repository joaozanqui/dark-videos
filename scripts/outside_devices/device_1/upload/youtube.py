import pyautogui as gui
from datetime import datetime
import pyperclip
import time
from scripts.outside_devices.device_1.utils import search_file

BUTTONS = {
# add
    "check_position": (300, 215),
    "create_button": (1800, 145),
    "send_video": (1800, 195),
    "upload_button": (950, 720),
    "check_position_2": (550, 330),
    "thumbnail_button": (600, 790),
    "title_box": (600, 400),
    "description_box": (670, 630),
    "next_button": (1350, 995),
    "off_button": (1000, 995),
    "not_for_kids": (540, 765),
# schedule
    "public": (585, 580),
    "schedule_option": (585, 690),
    "date_button": (690, 610),
    "time_button": (800, 610),
    "schedule_button": (1350, 995),
    "check_is_processing": (895, 700),
    "close_button": (1150, 745),
}

def goto_upload_page():
    gui.click(BUTTONS['create_button'])
    time.sleep(0.5)
    gui.click(BUTTONS['send_video'])
    time.sleep(1)

def select_video(channel_id, title_id, video_name):
    time.sleep(1)
    gui.click(BUTTONS['upload_button'])
    time.sleep(1)
    
    search_file(channel_id, title_id, video_name)

def select_image(channel_id, title_id):
    gui.click(BUTTONS['thumbnail_button'])
    time.sleep(1)
    file_name = 'thumbnail.png'
    search_file(channel_id, title_id, file_name, image=True)

def fill_text(title, description):
    while len(title) > 100:
        title = ' '.join(title.split(' ')[:-1])

    gui.click(BUTTONS['title_box'])
    gui.hotkey('ctrl', 'a')
    pyperclip.copy(title)
    gui.hotkey('ctrl', 'v')
    time.sleep(1)
        
    gui.click(BUTTONS['description_box'])
    gui.hotkey('ctrl', 'a')
    pyperclip.copy(description)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)

def go_next():
    gui.click(BUTTONS['off_button'])
    time.sleep(0.5)
    gui.click(BUTTONS['next_button'])
    time.sleep(0.5)
    gui.click(BUTTONS['not_for_kids'])
    time.sleep(0.5)
    gui.click(BUTTONS['next_button'])
    wait_page_load(BUTTONS['check_position_2'])
    gui.click(BUTTONS['next_button'])
    verifies_check = wait_page_load(BUTTONS['check_position_2'], limit=5)
    if not verifies_check:
        return False
    gui.click(BUTTONS['next_button'])
    wait_page_load(BUTTONS['check_position_2'])
    return True

def wait_page_load(button, limit=0):
    pyperclip.copy('')
    attempts = 0
    while pyperclip.paste() == '':
        time.sleep(5)
        gui.doubleClick(button)
        time.sleep(1)
        gui.hotkey('ctrl', 'c')
        attempts += 1
        if limit and attempts > limit:
            return False
    pyperclip.copy('')
    return True

def add_video(channel_id, title_id, title, description, video_name, shorts):
    wait_page_load(BUTTONS['check_position'])
    goto_upload_page()
    select_video(channel_id, title_id, video_name)
    wait_page_load(BUTTONS['check_position_2'])
    if not shorts:
        select_image(channel_id, title_id)
    fill_text(title, description)
    return go_next()    

# ---- schedule ----

def select_publish_time(hour, minute):    
    time_str = f"{hour}:{minute}"
    gui.click(BUTTONS["time_button"])
    time.sleep(0.5)

    gui.hotkey('ctrl', 'a')
    pyperclip.copy(time_str)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    gui.hotkey('enter')
    time.sleep(0.5)
    
def select_publish_date(publish_datetime):
    date = f"{publish_datetime.day}/{publish_datetime.month}/{publish_datetime.year}"
    
    gui.click(BUTTONS["date_button"])
    
    time.sleep(0.5)
    gui.hotkey('ctrl', 'a')
    pyperclip.copy(date)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    gui.hotkey('enter')
    time.sleep(0.5)

def schedule(publish_datetime):
    select_publish_date(publish_datetime)
    select_publish_time(str(publish_datetime.hour), str(publish_datetime.minute))   
    time.sleep(0.5)

def wait_video_process():
    pyperclip.copy('')
    while True:
        time.sleep(5)
        gui.doubleClick(BUTTONS['check_is_processing'])
        time.sleep(0.1) 
        gui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        clipboard_content = pyperclip.paste().strip()

        try:
            int(clipboard_content)
        except ValueError:
            break 

def handle_schedule(publish_datetime_str, shorts):
    time.sleep(1)
    gui.click(BUTTONS["public"])
    time.sleep(0.5)
    gui.click(BUTTONS["schedule_option"])
    time.sleep(0.5)
    publish_datetime = datetime.fromisoformat(publish_datetime_str)

    schedule(publish_datetime)
    gui.click(BUTTONS["schedule_button"])   
    time.sleep(10)
    if not shorts:
        wait_video_process()