import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import crop
from config.config import PIXABAY_API_KEYS
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
        response = requests.get(url, params=params)
        response.raise_for_status() 
        data = response.json()
        return data.get("hits", [])
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

def create_background_video(target_duration: float, temp_paths: list, video_orientation: str, video_query: str, target_resolution: tuple):
    clips = []
    total_duration = 0
    page = 1
    max_pages = 5
    DOWNLOAD_PAUSE_SECONDS = 5
    VIDEO_QUALITY = 'tiny'

    while total_duration < target_duration and page <= max_pages:
        api_key = next_pixabay_api_key()
        hits = fetch_pixabay_videos_page(video_orientation, video_query, page=page, api_key=api_key)
        if not hits:
            print("\t\t- No more videos found.")
            break
        
        random.shuffle(hits)

        for hit in hits:
            video_url = hit.get("videos", {}).get(VIDEO_QUALITY, {}).get("url")
            if not video_url:
                continue
            
            time.sleep(DOWNLOAD_PAUSE_SECONDS)
            
            filepath = None
            try:
                filepath = download_video_to_temp(video_url)
                if not filepath:
                    continue
                
                temp_paths.append(filepath)
                
                clip = VideoFileClip(filepath)
                processed_clip = resize_and_crop_clip(clip, target_resolution=target_resolution)
                
                clips.append(processed_clip)
                total_duration += processed_clip.duration
                print(f"\t\t\t- Current video duration: {total_duration:.2f}s / {target_duration}s")

                if total_duration >= target_duration:
                    break 
                
            except Exception as e:
                print(f"Erro ao processar o vídeo {video_url}: {e}")

        page += 1
        if total_duration < target_duration and page <= max_pages:
            time.sleep(DOWNLOAD_PAUSE_SECONDS)
            
    return clips

def run(duration, video_orientation='horizontal', video_query='drone', target_resolution=(1920, 1080)):
    print(f"\t\t-Building a {duration}s background video")

    if not PIXABAY_API_KEYS:
        raise ValueError("PIXABAY_API_KEYS not found in environment variables.")

    temp_paths = []
    try:
        selected_clips = create_background_video(duration, temp_paths, video_orientation=video_orientation, video_query=video_query, target_resolution=target_resolution)
                
        if not selected_clips:
            raise ValueError("No valid video found.")

        final_clip = concatenate_videoclips(selected_clips).subclip(0, duration).without_audio()
        return CompositeVideoClip([final_clip])
    finally:
        for path in temp_paths:
            try:
                os.unlink(path)
            except OSError as e:
                print(f"Error removing temp file {path}: {e}")