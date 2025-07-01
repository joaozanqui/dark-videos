import whisper
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import unicodedata
from pathlib import Path
from scripts.utils import get_final_language, get_language_code
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips
import random

def subtitles(audio_path, output_path):   
    os.makedirs(output_path, exist_ok=True)
    subtitles_file = f"{output_path}/subtitles.srt"
    
    if os.path.exists(subtitles_file):
        return subtitles_file 
    
    language = get_final_language()
    print("\t\t-Generating subtitles...")

    subtitles_dir = Path(output_path)
    subtitles_dir.mkdir(exist_ok=True)
    subtitles_path = subtitles_dir / f"subtitles.srt"
    model = whisper.load_model("medium")
    language_code = get_language_code(language)

    try:
        result = model.transcribe(
                    audio_path,
                    language=language_code,
                    # beam_size=3,
                    # best_of=3, 
                    # fp16=False  
                    verbose=False
                )   

        with open(subtitles_path, "w", encoding="utf-8") as subtitles_file:
            for i, segment in enumerate(result["segments"]):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()

                start_subtitiles = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02},{int(start_time%1*1000):03}"
                end_subtitles = f"{int(end_time//3600):02}:{int(end_time%3600//60):02}:{int(end_time%60):02},{int(end_time%1*1000):03}"

                subtitles_file.write(f"{i + 1}\n")
                subtitles_file.write(f"{start_subtitiles} --> {end_subtitles}\n")
                subtitles_file.write(f"{text}\n\n")

        print(f"\t\t-Subtitles generated successfull: {subtitles_path}")
        return str(subtitles_path)
    
    except Exception as e:
        print(f"Subtitles error: {e}")
        return None
    finally:
        del model

def music(audio_duration, mood):  
    print(f"\t\t-Merging background music ({audio_duration}s)...")
    musics_path = f"assets/musics/{mood}"

    mp3_files = [
        os.path.join(musics_path, f)
        for f in os.listdir(musics_path)
        if f.lower().endswith(".mp3")
    ]

    if not mp3_files:
        raise Exception(f"No music in found {musics_path}")

    random.shuffle(mp3_files)

    collected_clips = []
    total_duration = 0

    for music in mp3_files:
        try:
            clip = AudioFileClip(music)
        except Exception as e:
            print(f"Error loading {music}: {e}")
            continue

        collected_clips.append(clip)
        total_duration += clip.duration

        if total_duration >= audio_duration:
            break

    if not collected_clips:
        raise Exception("No valid music loaded.")

    merged = concatenate_audioclips(collected_clips)

    if merged.duration > audio_duration:
        merged = merged.subclip(0, audio_duration)
    
    final_music = merged.volumex(0.1) 
    return final_music

def is_emoji(char):
    emoji_blocks = {
        'EMOJIS_SUPPLEMENT', 'EMOJIS_EXTENDED_A', 'EMOJIS_EXTENDED_B',
        'MISCELLANEOUS_SYMBOLS_AND_PICTOGRAPHS',
        'EMOTICONS',
        'TRANSPORT_AND_MAP_SYMBOLS',
        'DINGBATS',
        'GEOMETRIC_SHAPES_EXTENDED',
        'SUPPLEMENTAL_SYMBOLS_AND_PICTOGRAPHS',
        'ORNAMENTAL_DINGBATS',
        'ALCHEMICAL_SYMBOLS',
        'PLAYING_CARDS',
    }
    
    if unicodedata.category(char) == 'So' or any(block in unicodedata.name(char, '') for block in emoji_blocks):
        return True
    
    if char in ['🏻', '🏼', '🏽', '🏾', '🏿', '♂', '♀']:
        return True

    if char == '\u200d':
        return True

    return False

def thumbnail(image_path: str, title: str, output_path: str):
    try:
        print(f"\t\t-Creating Thumbnail...")
        processed_title_chars = []
        for char in title:
            if not is_emoji(char):
                processed_title_chars.append(char)
        processed_title = "".join(processed_title_chars)

        image_dir = Path(image_path)
        background = Image.open(image_dir).convert("RGBA")
        width, height = background.size
        blurred_background = background.filter(ImageFilter.GaussianBlur(radius=8))
        draw = ImageDraw.Draw(blurred_background)
        
        font_path_text = "assets/font.ttf" 

        initial_fontsize = 80
        
        main_font = None 
        try:
            main_font = ImageFont.truetype(font_path_text, initial_fontsize)
        except IOError:
            print(f"\t\t-Warning: Text font '{font_path_text}' not found. Using default font.")
            main_font = ImageFont.load_default()

        max_line_width_chars = int(width / (initial_fontsize * 0.45)) 
        wrapped_title = textwrap.fill(processed_title, width=max_line_width_chars)

        max_text_container_width = int(width * 0.85)
        final_fontsize = initial_fontsize
        
        while True:
            temp_main_font = None
            try:
                temp_main_font = ImageFont.truetype(font_path_text, final_fontsize)
            except IOError:
                temp_main_font = ImageFont.load_default()
                
            lines = wrapped_title.split('\n')
            
            total_text_height = 0
            current_max_line_width = 0
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=temp_main_font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                total_text_height += line_height
                if line_width > current_max_line_width:
                    current_max_line_width = line_width
            
            if (current_max_line_width <= max_text_container_width and total_text_height < height * 0.75) or final_fontsize <= 30:
                main_font = temp_main_font
                break
            final_fontsize -= 5
            if final_fontsize < 30:
                try:
                    main_font = ImageFont.truetype(font_path_text, 30)
                except IOError:
                    main_font = ImageFont.load_default()
                break

        lines = wrapped_title.split('\n')
        total_text_height = 0
        current_max_line_width = 0
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=main_font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            total_text_height += line_height
            if line_width > current_max_line_width:
                current_max_line_width = line_width

        text_x_offset = (width - current_max_line_width) / 2
        text_y_start = (height - total_text_height) / 2

        
        padding = 40
        line_spacing = 10
        lines_padding = line_spacing * len(lines)
        box_x1 = text_x_offset - padding 
        box_y1 = text_y_start - padding
        box_x2 = text_x_offset + current_max_line_width + padding
        box_y2 = text_y_start + total_text_height + padding + lines_padding*2

        overlay = Image.new("RGBA", background.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0, 178))

        blurred_background = Image.alpha_composite(blurred_background, overlay)
        draw = ImageDraw.Draw(blurred_background) 

        current_y = text_y_start
        
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=main_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (width - line_width) / 2
            draw.text((line_x, current_y), line, font=main_font, fill=(255, 255, 255, 255))
            current_y += (line_bbox[3] - line_bbox[1]) + line_spacing
      

        output_dir = Path(output_path)
        blurred_background.save(output_dir)
        print(f"\t\t-Thumbnail created successful!")

    except FileNotFoundError as fnfe:
        print(f"Error thumbnail image: {image_dir} - {fnfe}")
    except Exception as e:
        print(f"Error thumbnail: {e}")