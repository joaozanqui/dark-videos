import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import crop
from config.keys import PIXABAY_API_KEYS
import random
import requests
import time
from tempfile import NamedTemporaryFile

PIXABAY_KEY = 0

def resize_and_crop_clip(clip, target_resolution):
    target_w, target_h = target_resolution
    target_aspect = target_w / target_h
    clip_aspect = clip.w / clip.h

    if clip_aspect > target_aspect:
        clip_resized = clip.resize(height=target_h)
    else:
        clip_resized = clip.resize(width=target_w)

    return crop(
        clip_resized,
        width=target_w,
        height=target_h,
        x_center=clip_resized.w / 2,
        y_center=clip_resized.h / 2
    )

def fetch_pixabay_videos_page(video_orientation, video_query, page=1, per_page=50, api_key=''):
    if not api_key:
        return
    
    print(f"\t\t\t- Finding videos at Pixabay API (Page {page})...")
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": video_query,
        "orientation": video_orientation,
        "per_page": per_page,
        "page": page
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status() 
        data = response.json()
        return data.get("hits", [])
    except requests.exceptions.Timeout:
        print("\t\t\t- Error at Pixabay API (timeout). Try again later...")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Pixabay API: {e}")
        return []

def download_video_to_temp(url: str):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        tmp = NamedTemporaryFile(delete=False, suffix=".mp4")
        with tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
        return tmp.name
    except requests.exceptions.RequestException as e:
        print(f"\t\t\t\t- Error: {e}")
        return None
    
def next_pixabay_api_key():
    global PIXABAY_KEY
    max_key = len(PIXABAY_API_KEYS) - 1
    PIXABAY_KEY += 1
    
    if PIXABAY_KEY > max_key:
        PIXABAY_KEY = 0
    
    return PIXABAY_API_KEYS[PIXABAY_KEY]

def select_random_page(all_pages, checked_pages):
    available_pages = [page for page in all_pages if page not in checked_pages]
    chosen_page = random.choice(available_pages)

    return chosen_page


def create_background_video(target_duration: float, temp_paths: list, video_orientation: str, video_query: str, target_resolution: tuple):
    clips = []
    total_duration = 0
    all_pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    checked_pages = []
    
    DOWNLOAD_PAUSE_SECONDS = 5
    VIDEO_QUALITY = 'tiny'
    BATCH_TARGET_DURATION = 600
    
    batch_files = []
    batch_clips = []
    batch_duration = 0
    batch_number = 1

    while total_duration < target_duration and len(checked_pages) < len(all_pages):
        page = select_random_page(all_pages, checked_pages)
        checked_pages.append(page)
        api_key = next_pixabay_api_key()
        hits = fetch_pixabay_videos_page(video_orientation, video_query, page=page, api_key=api_key)
        
        if not hits:
            continue
        
        random.shuffle(hits)

        for hit in hits:
            if total_duration >= target_duration:
                break
            
            video_url = hit.get("videos", {}).get(VIDEO_QUALITY, {}).get("url")
            if not video_url:
                continue
            
            time.sleep(DOWNLOAD_PAUSE_SECONDS)
            filepath = download_video_to_temp(video_url)
            if not filepath:
                continue

            try:
                temp_paths.append(filepath)
                clip = VideoFileClip(filepath)
                processed_clip = resize_and_crop_clip(clip, target_resolution=target_resolution)
                
                batch_clips.append(processed_clip)
                batch_duration += processed_clip.duration
                total_duration += processed_clip.duration
                
                print(f"\t\t\t- Total duration: {total_duration:.2f}s / {target_duration:.2f}s")

                if batch_duration >= BATCH_TARGET_DURATION:
                    batch_filepath = f"temp_batch_{batch_number}.mp4"
                    batch_video = concatenate_videoclips(batch_clips)
                    batch_video.write_videofile(batch_filepath, codec='libx264', preset='ultrafast', threads=os.cpu_count())
                    
                    for c in batch_clips:
                        c.close()

                    batch_files.append(batch_filepath)
                    temp_paths.append(batch_filepath)
                    batch_clips = []
                    batch_duration = 0
                    batch_number += 1
            
            except Exception as e:
                print(f"Error processing {video_url}: {e}")

    if not batch_files and batch_clips:
        return batch_clips

    if batch_clips:
        batch_filepath = f"temp_batch_{batch_number}.mp4"
        batch_video = concatenate_videoclips(batch_clips)
        batch_video.write_videofile(batch_filepath, codec='libx264', preset='ultrafast', threads=os.cpu_count())
        for c in batch_clips:
            c.close()
        batch_files.append(batch_filepath)
        temp_paths.append(batch_filepath)

    for batch_file in batch_files:
        clips.append(VideoFileClip(batch_file))

    return clips

def run(duration, video_orientation='horizontal', video_query='drone', target_resolution=(1920, 1080)):
    print(f"\t\t-Building a {duration:.2f}s background video")
    if not PIXABAY_API_KEYS:
        raise ValueError("PIXABAY_API_KEYS not found.")

    temp_paths = []
    final_clip_obj = None
    selected_clips = []
    try:
        selected_clips = create_background_video(duration, temp_paths, video_orientation, video_query, target_resolution)
        if not selected_clips:
            raise ValueError("No valid video found.")

        concatenated_clip = concatenate_videoclips(selected_clips)
        safe_duration = min(concatenated_clip.duration, duration)
        final_clip = concatenated_clip.subclip(0, safe_duration).without_audio()
        final_clip_obj = CompositeVideoClip([final_clip])
    finally:
        for path in temp_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError as e:
                print(f"Error removing temp file {path}: {e}")
    
    return final_clip_obj, selected_clips