import os
from moviepy.editor import ImageClip, CompositeVideoClip
from datetime import datetime
from moviepy.video.fx.all import mask_color

def parse_srt_time(time_str):
    t = datetime.strptime(time_str, "%H:%M:%S,%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1_000_000

def run(expressions_path, subtitles_with_expressions, duration, position_h=-200, position_v='center', expressions_size=1.2):
    print("\t\t- Building the expressions videofile...")
    image_clips = []

    for entry in subtitles_with_expressions:
        expression_name = entry["expression"]
        
        start = entry["start"]
        if isinstance(start, str):
            start = parse_srt_time(start)
        end = entry["end"]
        if isinstance(end, str):
            end = parse_srt_time(end)

        image_duration = end - start
        image_path = os.path.join(expressions_path, f"{expression_name}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join(expressions_path, f"serious.png")

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
    
    expressions_position=(position_h, position_v)
    expressions_video = expressions_video.resize(expressions_size)
    expressions_video = expressions_video.set_position(expressions_position)

    return expressions_video