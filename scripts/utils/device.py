from pathlib import Path
import os

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