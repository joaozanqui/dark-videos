from pathlib import Path
import scripts.database as database
import scripts.utils.device as device
import scripts.images.thumbnail as thumbnail
from typing import Optional
import shutil
import os
import pyperclip
import time


def copy_image_to_right_path(final_path: str) -> Optional[Path]:
    try:        
        last_file = device.get_last_downloaded_file()
        ext = last_file.suffix.lstrip(".")
        if not ext in database.ALLOWED_IMAGES_EXTENSIONS:
            ext = 'png'

        file_name = f"image.{ext}"

        full_path = Path.cwd() / final_path
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

def run(channel_id):
    # https://www.freepik.com/pikaso/ai-image-generator
    channel = database.get_item('channels', channel_id)
    titles = database.channel_titles(channel_id)

    print(f"Channel: '{channel['name']}'")
    for title in titles:
        video = database.get_item('videos', title['id'], column_to_compare='title_id')
        if video['has_image']:
            continue

        final_path = f"storage/{channel_id}/{title['title_number']}"

        try:
            last_file_before_download = device.get_last_downloaded_file()
            last_file = device.get_last_downloaded_file()

            os.makedirs(final_path, exist_ok=True)

            image_prompt = video['thumbnail_prompt']
            print(f"{channel_id}/{title['title_number']}:\n{image_prompt}")
            pyperclip.copy(image_prompt)

            while last_file == last_file_before_download:
                time.sleep(5)
                last_file = device.get_last_downloaded_file()
            
            image_path = copy_image_to_right_path(final_path)
            
            if not image_path:
                print("Error coping image...")
                return None
            database.update('videos', video['id'], 'has_image', True)

            output_thumbnail_path = f"{final_path}/thumbnail.png"
            if thumbnail.build(image_path, output_thumbnail_path, channel_id, video['thumbnail_data']):
                database.update('videos', video['id'], 'has_thumbnail', True)
            print("Successful!\n\n")

        except Exception as e:
            print(f"Error {channel_id}/{title['title_number']}: {e}")

