import os
from moviepy.editor import ImageClip, CompositeVideoClip
from datetime import datetime
from moviepy.video.fx.all import mask_color

def parse_srt_time(time_str):
    t = datetime.strptime(time_str, "%H:%M:%S,%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000

def run(expressions_path, subtitles_with_expressions, duration):
    image_clips = []

    for entry in subtitles_with_expressions:
        expression_name = entry["expression"]
        start = parse_srt_time(entry["start"])
        end = parse_srt_time(entry["end"])
        image_duration = end - start

        image_path = os.path.join(expressions_path, f"{expression_name}.png")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Expression '{expression_name}' not found at: {image_path}")

        image_clip = (
            ImageClip(image_path)
            .set_duration(image_duration)
            .set_start(start)
            .set_position("center")
            .fx(mask_color, color=[0,255,0], thr=100, s=5)
        )
        image_clips.append(image_clip)

    expressions_video = CompositeVideoClip(image_clips, size=None, bg_color=None)
    expressions_video = expressions_video.set_duration(duration)
    
    expressions_position=(-200, 'center')
    expressions_video = expressions_video.resize(1.2)
    expressions_video = expressions_video.set_position(expressions_position)

    return expressions_video