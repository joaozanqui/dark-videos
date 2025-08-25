from pathlib import Path
from typing import Optional
import shutil
import re
import time
from typing import List, Union

def copy_audio_to_right_path(file_name: str, final_path: str, audio_file: Path) -> Optional[Path]:
    max_retries = 5
    retry_delay = 2
    time.sleep(5)
    for attempt in range(max_retries):
        print(audio_file)
        try:
            time.sleep(2)
            file_name = file_name + '.mp3'

            full_path = Path.cwd() / final_path
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / file_name
            
            shutil.copy2(audio_file, file_path)

            return file_path

        
        except PermissionError:
            print(f"\nAttempt {attempt + 1} of {max_retries}: Permission denied. The file '{audio_file}' might be in use.")
            if attempt + 1 < max_retries:
                print(f"Retrying in {retry_delay} second(s)...")
                time.sleep(retry_delay)
            else:
                print("\nFailed to copy the file after multiple attempts. Please check if it is being used by another program.")
                return None
            
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            return None


def divide_text(
    full_text: str,
    max_chars: int = 10000,
    separate_character: Union[str, List[str]] = '\n'
) -> List[str]:
    
    if isinstance(separate_character, str):
        separate_character = [separate_character]
    
    sep_pattern = "(" + "|".join(map(re.escape, separate_character)) + ")"
    
    result = []
    start = 0
    length = len(full_text)

    while start < length:
        if length - start <= max_chars:
            result.append(full_text[start:])
            break
        
        end = start + max_chars
        
        match_iter = list(re.finditer(sep_pattern, full_text[start:end]))
        
        if match_iter:
            last_match = match_iter[-1]
            cut_pos = last_match.end()
            result.append(full_text[start:start+cut_pos])
            start += cut_pos
        else:
            space_iter = list(re.finditer(" ", full_text[start:end]))
            if space_iter:
                last_space = space_iter[-1]
                cut_pos = last_space.end()
                result.append(full_text[start:start+cut_pos])
                start += cut_pos
            else:
                result.append(full_text[start:end])
                start = end
    
    return result