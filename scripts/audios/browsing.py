import pyautogui as gui
import pyperclip
import time

screenWidth, screenHeight = gui.size()
has2screens = screenWidth == 3840

# browser:
def goto_bottom_of_page(x=1):
    gui.scroll(-screenHeight*x)
    time.sleep(0.5)

def goto_top_of_page(x=1):
    gui.scroll(screenHeight*x)
    time.sleep(0.5)
    
        
def reset_zoom():
    gui.hotkey('ctrl', '+')
    time.sleep(0.5)
    reset_button = (1650, 110)
    gui.click(reset_button)
    
def goto_page(page):
    time.sleep(0.5)
    browser_search_box = (700, 65)
    gui.click(browser_search_box)
    pyperclip.copy(page)
    time.sleep(1)
    gui.hotkey('ctrl', 'v')
    gui.press('enter')    
    time.sleep(5)

def open_browser(browser, system):
    time.sleep(2)
    gui.press('win') 
    time.sleep(2)
    
    gui.write(browser)    
    time.sleep(1)
    gui.press('enter')
    time.sleep(2)

    reset_zoom()
    time.sleep(0.5)
    
    return True
