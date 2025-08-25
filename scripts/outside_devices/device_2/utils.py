import pyautogui as gui
import time
import pyperclip

BUTTONS = {
    "search_folder_box": (1400, 45),
    "search_file_box": (1760, 45),
    "first_result": (250, 120),
    "browser_search_box": (700, 60),
}

screenWidth, screenHeight = gui.size()

def search_file(file_path, file_name):
    gui.click(BUTTONS['search_folder_box'])
    pyperclip.copy(file_path)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    gui.hotkey('enter')
    time.sleep(1)

    gui.click(BUTTONS['search_file_box'])
    pyperclip.copy(file_name)
    gui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    gui.hotkey('enter')
    time.sleep(1)

    gui.doubleClick(BUTTONS['first_result'])
    time.sleep(2)


def wait_process(check_button, time_sleep=5, clicks_qty=2):
    pyperclip.copy('')
    empty_text = pyperclip.paste().strip()
    
    while True:
        time.sleep(time_sleep)
        if clicks_qty == 1:
            gui.click(check_button)
        if clicks_qty == 2:
            gui.doubleClick(check_button)
        if clicks_qty == 3:
            gui.tripleClick(check_button)
        time.sleep(0.1) 
        gui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        clipboard_content = pyperclip.paste().strip()
        if clipboard_content != empty_text:
            break

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
# colocar no scripts.upload.utils