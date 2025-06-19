import audios.browsing as browsing
import audios.capcut as capcut
from typing import List
from pydub import AudioSegment

def divide_text(full_text: str, max_chars: int = 10000) -> List[str]:
    paragraphs = [p for p in full_text.split('\n') if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if not current_chunk:
            current_chunk = paragraph

        elif len(current_chunk) + len(paragraph) + 1 <= max_chars:
            current_chunk += '\n' + paragraph
        else:
            chunks.append(current_chunk)
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def merge_audio(audios_paths):
    audio_final = AudioSegment.empty()

    for path in audios_paths:
        audio = AudioSegment.from_file(path)
        audio_final += audio 

    final_path = "storage/audios/final_audio.mp3"
    audio_final.export(final_path, format="mp3")
    
    return final_path

def run(full_text=None):
    if not full_text:
        with open('storage/scripts/full_script.txt', "r", encoding="utf-8") as file:
            full_text = file.read() 
            
    capcut_generate_audio_page = 'https://www.capcut.com/magic-tools/text-to-speech'

    texts = divide_text(full_text)
    browsing.open_browser(browser='Google Chrome', system='ubuntu')
    browsing.goto_page(capcut_generate_audio_page)
    audios_paths = capcut.run(texts)
    audio_path = merge_audio(audios_paths)
        
    return audio_path