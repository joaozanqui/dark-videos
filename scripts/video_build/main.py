import os
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import scripts.video_build.generate as generate
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
import scripts.shorts.main as shorts
import gc
import scripts.database as database

def render_video(audio, video, final_path, file_name='video'):    
    output_path = f"{final_path}/videos"
    os.makedirs(output_path, exist_ok=True)
    output_file = f"{output_path}/{file_name}.mp4"

    video.audio = audio
    video.fps = 24
    gc.collect()
    
    print(f"\t\t-Exporting final video: {output_file}")
    
    video.write_videofile(
        output_file, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='audio.m4a',
        remove_temp=True,
        threads=2,
        preset='ultrafast'
    )
    
    print("\t\t-Video built successful!")

def create_subtitles(background_video_composite, subtitles, padding, denominators):
    w_denominator, h_denominator = denominators
    if w_denominator == 0:
        w_denominator = 1
    if h_denominator == 0:
        h_denominator = 1

    def subtitle_generator(txt):
        return TextClip(
            txt,
            font='assets/font.ttf',
            fontsize=64,
            color='yellow',
            method='caption',
            align='center',
            size=(int(background_video_composite.w * padding), None),
            bg_color='rgba(0, 0, 0, 0.6)',
        )
    
    subtitles_data = [
        ((sub['start'], sub['end']), sub['text'])
        for sub in subtitles
    ]

    subtitles_clip = SubtitlesClip(subtitles_data, subtitle_generator)
    subtitles_x = int(background_video_composite.w // w_denominator)
    subtitles_y = int(background_video_composite.h // h_denominator)
    subtitles_clip = subtitles_clip.set_position((subtitles_x, subtitles_y))
    subtitles_clip = subtitles_clip.set_duration(background_video_composite.duration)
    return subtitles_clip

def create_video(
    background_video_composite: CompositeVideoClip,
    expressions_images_composite: CompositeVideoClip,
    subtitles: list,
    intro_file = '',
    subtitles_padding=0.45,
    subtitles_denominators=(2, 2.5)
):
    print("\t\t- Merging Video...")
    concatenate_intro = intro_file != ''

    subtitles = create_subtitles(background_video_composite, subtitles, padding=subtitles_padding, denominators=subtitles_denominators)
    main_video = CompositeVideoClip([
        background_video_composite,
        expressions_images_composite,
        subtitles
    ])

    if concatenate_intro and os.path.exists(intro_file):
        intro_clip = VideoFileClip(intro_file)
        final_video = concatenate_videoclips([intro_clip, main_video])
    else:
        final_video = main_video

    return final_video

def create_audio(narration_audio: AudioFileClip, background_music: AudioFileClip, intro_file = ''):
    print("\t\t- Merging Audio...")
    concatenate_intro = intro_file != ''

    background_music = background_music.volumex(0.5)
    main_audio = CompositeAudioClip([narration_audio, background_music])

    if concatenate_intro and os.path.exists(intro_file):
        intro_audio = AudioFileClip(intro_file)
        final_audio = concatenate_audioclips([intro_audio, main_audio])
    else:
        final_audio = main_audio

    return final_audio


def fix_subtitles_time(subtitles):
    last_end = '00:00:00,000'
    for subtitle in subtitles:
        subtitle['start'] = last_end
        last_end = subtitle['end']
    
    return subtitles


def build_video(final_path, channel, video, language):
    audio_path = f"{final_path}/audio.mp3"
    narration_audio = AudioFileClip(audio_path)
    background_music = generate.music(audio_duration=narration_audio.duration ,mood=channel['mood'])

    if not video['subtitles']:
        video['subtitles'] = generate.subtitles(audio_path, language, video['id'])

    if not video['expressions']:
        video['expressions'] = generate.expressions(video['subtitles'], channel['id'], video['id'])

    subtitles = fix_subtitles_time(video['expressions'])

    background_video_composite = background_video.run(narration_audio.duration)
    expressions_path = f"assets/expressions/{channel['id']}/chroma"
    expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration)
    intro_file = f"assets/intros/{channel['id']}/intro.mp4"

    audio = create_audio(narration_audio, background_music, intro_file=intro_file)
    video = create_video(background_video_composite, expressions_images_composite, video['subtitles'], intro_file=intro_file)
    render_video(audio, video, final_path)

def run(channel_id):
    collected_objects = gc.collect()
    print("--- Building Videos ---\n")
    channel = database.get_item('channels', channel_id)

    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    for title in titles:
        video = database.get_item('videos', title['id'], column_to_compare='title_id')
        if video['uploaded']:
            continue
        
        print(f"\t-(Channel: {channel_id} / Title: {title['title_number']}) {title['title']}")
        final_path = f"storage/{channel_id}/{title['title_number']}"
        
        if not video['has_audio'] or not video['description']:
            continue

        if video['generated_device']:
            device = database.get_item('devices', video['generated_device'])
            print(f"\t\t-Video file already exists in device '{device['name']}'!")
            continue
        try:  
            language = database.get_item('languages', channel['language_id'])
            build_video(final_path, channel, video, language['name'])
            database.update('videos', video['id'], 'generated_device', database.DEVICE)

            subtitles_top = channel['shorts_subtitles_position'] == 'top'
            shorts.build(channel, title, subtitles_top)
        finally:
            print("\t- Cleaning up memory before next iteration...")
            collected_objects = gc.collect()
            print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
            print("-" * 40)

    
    print("\n--- Process Finished ---")
