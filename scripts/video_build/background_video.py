import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import crop
from config.config import PIXABAY_API_KEY
import random
import requests
from tempfile import NamedTemporaryFile

def get_total_hits(query="drone", orientation="horizontal"):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "orientation": orientation,
        "per_page": 3,
        "page": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data["totalHits"]

def search_pixabay_videos(query="drone", orientation="horizontal", per_page=50, page=1):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "orientation": orientation,
        "per_page": per_page,
        "page": page
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["hits"]

def download_video(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    tmp = NamedTemporaryFile(delete=False, suffix=".mp4")
    for chunk in response.iter_content(chunk_size=8192):
        tmp.write(chunk)
    tmp.close()
    return tmp.name


def resize_and_crop_clip(clip, target_resolution=(1920, 1080)):
    target_w, target_h = target_resolution

    if clip.w / clip.h < target_w / target_h:
        clip_resized = clip.resize(height=target_h)
    else:
        clip_resized = clip.resize(width=target_w)

    return crop(
        clip_resized,
        width=target_w,
        height=target_h,
        x_center=clip_resized.w // 2,
        y_center=clip_resized.h // 2
    )

def merge_videos(duration, temp_paths):
    total_hits = get_total_hits()
    per_page = 50
    total_pages = max(1, total_hits // per_page)
    total_duration = 0
    selected_clips = []

    attempts = 0
    max_attempts = 10 * total_pages

    while total_duration < duration and attempts < max_attempts:
        attempts += 1
        random_page = random.randint(1, total_pages)
        hits = search_pixabay_videos(page=random_page, per_page=per_page)
        random.shuffle(hits)

        for hit in hits:
            # qualities = ['large', 'medium', 'small', 'tiny']
            # quality = random.choice(list(hit["videos"].keys()))
            quality = 'tiny'
            video_url = hit["videos"][quality]["url"]
            try:
                filepath = download_video(video_url)
                temp_paths.append(filepath)
                clip = VideoFileClip(filepath)
                clip = resize_and_crop_clip(clip, target_resolution=(1920, 1080))
                selected_clips.append(clip)
                total_duration += clip.duration
                
                print(f"\t\t\t{total_duration:.2f}s/{duration}s")

                if total_duration >= duration:
                    break

            except Exception as e:
                print(f"Erro ao processar vídeo: {e}")

    return selected_clips

def run(duration, output_path):
    output_video_path = f"{output_path}/background_video.mp4"
    if os.path.exists(output_video_path):
        return output_video_path

    print(f"\t\t-Building a {duration}s background video")

    if PIXABAY_API_KEY is None:
        raise ValueError("PIXABAY_API_KEY not found in environment variables.")

    temp_paths = []
    selected_clips = merge_videos(duration, temp_paths)
            
    if not selected_clips:
        raise ValueError("Nenhum vídeo válido foi encontrado.")

    final_clip = concatenate_videoclips(selected_clips).subclip(0, duration).without_audio()
    return CompositeVideoClip([final_clip])
