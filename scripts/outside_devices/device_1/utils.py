import pyautogui as gui
import scripts.database as database
import config.keys as keys
import time
import pyperclip

BUTTONS = {
    "documents_folder": (600, 580),
    "desktop_folder": (600, 530),
    "search_button": (1260, 405),
    "search_box": (1150, 455),
    "first_result": (750, 515),
    "browser_search_box": (700, 95),
}

screenWidth, screenHeight = gui.size()

def search_file(channel_id, title_number, file_name, image=False):
    device_id = keys.DEVICE
    device = database.get_item('devices', device_id)
    final_paths = device['final_path'].split('/')[3:]
    final_paths.append(str(channel_id))
    final_paths.append(str(title_number))
    if not image:
        final_paths.append('videos')
    final_paths.append(file_name)

    root = final_paths.pop(0)
    root_folder = f"{root.lower()}_folder"
    gui.click(BUTTONS[root_folder])
    time.sleep(1)
    for folder in final_paths:
        gui.click(BUTTONS['search_button'])
        time.sleep(1)
        gui.click(BUTTONS['search_box'])
        time.sleep(1)
        pyperclip.copy(f"{folder.lower()}")
        gui.hotkey('ctrl', 'v')
        time.sleep(1)
        gui.doubleClick(BUTTONS['first_result'])
        time.sleep(1)


    gui.hotkey('enter')
    gui.doubleClick(BUTTONS['first_result'])
    time.sleep(1)

def goto_bottom_of_page(x=1, time_sleep=0.5):
    gui.scroll(-screenHeight*x)
    time.sleep(time_sleep)

def goto_top_of_page(x=1, time_sleep=0.5):
    gui.scroll(screenHeight*x)
    time.sleep(time_sleep)

def goto_page(page):
    time.sleep(0.5)
    gui.click(BUTTONS["browser_search_box"])
    pyperclip.copy(page)
    time.sleep(1)
    gui.hotkey('ctrl', 'v')
    gui.press('enter')    
    time.sleep(0.5)
    gui.hotkey('space')
    time.sleep(0.5)
    gui.press('enter')    
    time.sleep(5)
