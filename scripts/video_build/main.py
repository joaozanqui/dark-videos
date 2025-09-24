import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.audio.AudioClip import AudioArrayClip
import scripts.video_build.generate as generate
import scripts.video_build.background_video as background_video
import scripts.video_build.expressions_images as expressions_images
import scripts.shorts.main as shorts
import gc
import scripts.database as database
import config.keys as keys

def render_video(audio_path, video, final_path, source_clips, file_name='video'):
    output_path = f"{final_path}/videos"
    os.makedirs(output_path, exist_ok=True)
    output_file = f"{output_path}/{file_name}.mp4"

    audio = AudioFileClip(audio_path)
    video.audio = audio
    video.fps = 24
    
    print(f"\t\t-Exporting final video: {output_file}")
    
    video.write_videofile(
        output_file, 
        codec='libx264', 
        audio_codec='aac',
        temp_audiofile='audio.m4a',
        remove_temp=True,
        threads=4,
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

def create_audio(narration_audio: AudioFileClip, channel: dict, intro_file = '', final_path = ''):
    if database.has_file(final_path):
        return final_path
    
    print("\t\t- Merging Audio...")
    background_music = generate.music(audio_duration=narration_audio.duration, mood=channel['mood'])
    concatenate_intro = intro_file != ''

    background_music = background_music.volumex(0.65)
    main_audio = CompositeAudioClip([narration_audio, background_music])
    main_audio = main_audio.set_duration(narration_audio.duration)

    if concatenate_intro and os.path.exists(intro_file):
        intro_audio = AudioFileClip(intro_file)
        final_audio = concatenate_audioclips([intro_audio, main_audio])
    else:
        final_audio = main_audio

    if final_path:
        final_audio.write_audiofile(final_path, fps=narration_audio.fps)
        return final_path
    
    return final_audio

def fix_subtitles_time(subtitles):
    last_end = '00:00:00,000'
    for subtitle in subtitles:
        subtitle['start'] = last_end
        last_end = subtitle['end']
    
    return subtitles

def get_narration_audio(temp_audio_path):
    print(f"\t\t- Processed audio file found. Loading from: {temp_audio_path}")
    try:
        y, sr = librosa.load(temp_audio_path, sr=None, mono=True)
        final_audio_reshaped = y.reshape(-1, 1)
        narration_audio = AudioArrayClip(final_audio_reshaped, fps=sr)
        print(f"\t\t- Audio clip loaded successfully! Duration: {narration_audio.duration:.2f}s")
        return narration_audio
    except Exception as e:
        print(f"\t\t- Error loading existing temp audio file: {e}. Reprocessing...")

def remove_pauses(audio_path, temp_audio_path, top_db=40, min_pause_duration_seconds=3.0):        
    print(f"\t\t- Removing audio pauses...")
    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
    except Exception as e:
        print(f"\t\t- Error loading audio file: {e}")
        return None, None

    sound_intervals = librosa.effects.split(y, top_db=top_db)

    if not sound_intervals.any():
        print(f"\t\t- No sound detected in the file.")
        return None, None

    audio_chunks = []
    start, end = sound_intervals[0]
    audio_chunks.append(y[start:end])

    for i in range(len(sound_intervals) - 1):
        end_of_current_chunk = sound_intervals[i][1]
        start_of_next_chunk = sound_intervals[i+1][0]
        silence_duration_samples = start_of_next_chunk - end_of_current_chunk
        if silence_duration_samples < min_pause_duration_seconds:
            audio_chunks.append(y[end_of_current_chunk:start_of_next_chunk])
        next_start, next_end = sound_intervals[i+1]
        audio_chunks.append(y[next_start:next_end])

    final_audio = np.concatenate(audio_chunks)

    if final_audio.size > 0:
        sf.write(temp_audio_path, final_audio, sr)
        final_audio_reshaped = final_audio.reshape(-1, 1)
        narration_audio = AudioArrayClip(final_audio_reshaped, fps=sr)
        
        print(f"\t\tAudio clip created in memory successfully! Duration: {narration_audio.duration:.2f}s")
        
        return narration_audio
    else:
        print("\t\tNo audio left after silence removal. Clip was not created.")
        return None, None

def run_preprocess(audio_path, temp_audio_path, channel, video):
    if database.has_file(temp_audio_path) and video['subtitles'] and video['expressions']:
        print(f"\t\tPreprocess done!")
        return False
    
    print(f"\t\t--- Preparing Videos ---\n")
    
    if not database.has_file(temp_audio_path):
        removed = remove_pauses(audio_path, temp_audio_path)
        if not removed:
            return False
    
    if not video['subtitles']:
        language = database.get_item('languages', channel['language_id'])
        video['subtitles'] = generate.subtitles(temp_audio_path, language['name'], video['id'])
        if not video['subtitles']:
            return False

    if not video['expressions']:
        video['expressions'] = generate.expressions(video['subtitles'], channel['id'], video['id'])

    return True

def build(final_path, temp_audio_path, channel, video):
    narration_audio = get_narration_audio(temp_audio_path)
    intro_file = f"assets/intros/{channel['id']}/intro.mp4"

    audio_path = create_audio(narration_audio, channel, intro_file=intro_file, final_path=f"{final_path}/final_audio.mp3")
    
    expressions_path = f"assets/expressions/{channel['id']}/chroma"
    subtitles = fix_subtitles_time(video['expressions'])
    expressions_images_composite = expressions_images.run(expressions_path, subtitles, narration_audio.duration)
    
    background_video_composite, clips_to_close = background_video.run(narration_audio.duration)

    video = create_video(background_video_composite, expressions_images_composite, video['subtitles'], intro_file=intro_file)
    render_video(audio_path, video, final_path, clips_to_close)

def run(channel_id, preprocess=False):
    collected_objects = gc.collect()
    process_name = 'Preparing' if preprocess else 'Building'
    print(f"\n- {process_name} Videos")
    
    channel = database.get_item('channels', channel_id)
    print(f"- {channel['name']}\n")
    titles = database.channel_titles(channel_id)

    for title in titles:
        video = database.get_item('videos', title['id'], column_to_compare='title_id')
        if not video or video['uploaded']:
            continue

        print(f"\t-(Channel: {channel['id']} / Title: {title['title_number']}) {title['title']}")

        if video['generated_device']:
            device = database.get_item('devices', video['generated_device'])
            print(f"\t\t- Video file already exists in device '{device['name']}'!")
            shorts.run(video, channel, title, preprocess)            
            continue
        
        
        if not video['has_audio'] or not video['description']:
            print(f"\t\tCouldn`t find video AUDIO and DESCRIPTIONS")
            continue

        try:  
            final_path = f"storage/{channel['id']}/{title['title_number']}"
            audio_path = f"{final_path}/audio.mp3"
            temp_audio_path = f"{final_path}/resized_audio.mp3"
        
            is_preprocessed = False
            if preprocess:
                is_preprocessed = run_preprocess(audio_path, temp_audio_path, channel, video)
            else:
                build(final_path, temp_audio_path, channel, video)
                database.update('videos', video['id'], 'generated_device', keys.DEVICE)
            
            shorts.run(video, channel, title, preprocess)     
            
            if is_preprocessed or not preprocess:
                print(f"\t\t- {process_name} Process Finished ---")       
        finally:
            collected_objects = gc.collect()
            print(f"\t\t- Memory cleanup complete. Freed {collected_objects} objects.")
