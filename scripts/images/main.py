from pathlib import Path
import json
from typing import Optional
from scripts.utils import get_last_downloaded_file
import shutil
from scripts.utils import ALLOWED_EXTENSIONS

# def rename_images(channel, video):
#     final_path = Path("storage/images") / channel / video

#     image_files = [
#         f for f in final_path.iterdir() 
#         if f.is_file() and f.suffix.lstrip(".").lower() in ALLOWED_EXTENSIONS
#     ]

#     if not image_files:
#         print("Erro: Nenhuma imagem (.png, .jpg, .jpeg) encontrada na pasta.")
#         return False
    
#     if len(image_files) > 1:
#         print(f"Aviso: Múltiplas imagens encontradas. Renomeando a primeira: '{image_files[0].name}'")

#     file_to_rename = image_files[0]

#     ext = file_to_rename.suffix.lstrip(".")
#     new_name = f"image.{ext}"
#     new_path = final_path / new_name

#     file_to_rename.rename(new_path)

#     print(f"Sucesso! O arquivo '{file_to_rename.name}' foi renomeado para '{new_name}'.")
#     return True



def copy_image_to_right_path(final_path: str) -> Optional[Path]:
    try:        
        last_file = get_last_downloaded_file()
        ext = last_file.suffix.lstrip(".")
        if not ext in ALLOWED_EXTENSIONS:
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

def run():
    # https://www.freepik.com/pikaso/ai-image-generator
    path = Path("storage/thought")
    channels_path = "storage/ideas/channels.json"

    with open(channels_path, "r", encoding="utf-8") as file:
        channels = json.load(file)

    if not path.is_dir():
        print(f"Error: No video generated.")
        return

    for channel in sorted(path.iterdir(), key=lambda p: int(p.name)):
        if channel.is_dir():
            print(f"Channel: '{channels[int(channel.name)]['name']}'")
            for video in sorted(channel.iterdir(), key=lambda p: int(p.name)):              
                if video.is_dir():
                    try:
                        final_path = f"storage/images/{channel.name}/{video.name}"

                        image_files = [
                            f for f in Path(final_path).iterdir() 
                            if f.suffix.lstrip(".").lower() in ALLOWED_EXTENSIONS
                        ]

                        if image_files:
                            continue

                        prompt_file_path = video / "image_prompt.txt"
                        image_prompt = prompt_file_path.read_text(encoding="utf-8").strip()
                        print(f"{channel.name}/{video.name}:\n{image_prompt}")
                        input("--> Copy the prompt, generate the image and save it at 'Downloads' folder.\n--> Press 'Enter' when the image is in 'Downloads' dir")
                        copied = copy_image_to_right_path(final_path)
                        
                        if not copied:
                            print("Error coping image...")
                            return None
                        print("Successful!\n\n")

                    except Exception as e:
                        print(f"Error {channel.name}/{video.name}: {e}")
    
    