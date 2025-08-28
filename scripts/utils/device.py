from pathlib import Path
import os
import time

def get_last_downloaded_file():
    downloads_path = Path.home() / 'Downloads'
    
    if not downloads_path.exists() or not downloads_path.is_dir():
        downloads_path = Path.home() / 'Transferências'
        if not downloads_path.exists() or not downloads_path.is_dir():
            return None
    
    files = [f for f in downloads_path.iterdir() if f.is_file() and not str(f).endswith(('.tmp', '.crdownload'))]

    if not files:
        return None

    last_file = max(files, key=os.path.getctime)
    return last_file 

def wait_for_new_file(previous_latest_file, timeout=120):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_latest_file = get_last_downloaded_file()
        if current_latest_file and current_latest_file != previous_latest_file:
            time.sleep(1)
            last_size = -1
            while True:
                try:
                    current_size = os.path.getsize(current_latest_file)
                    if current_size == last_size and current_size > 0:
                        return current_latest_file
                    last_size = current_size
                    time.sleep(1)
                except Exception as e:
                    current_latest_file = get_last_downloaded_file()
                    continue
        time.sleep(1)
    return None