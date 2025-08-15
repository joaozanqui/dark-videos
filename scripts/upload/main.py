import scripts.database as database
import scripts.upload.browsing as browsing
import scripts.upload.youtube as youtube
import os
from datetime import datetime, timedelta

def upload_single_video(channel, title_id, video_title, video_description, video_name, publish_time, shorts):
    browsing.goto_page(page=channel['upload_url'])
    video_added = youtube.add_video(channel['id'], title_id, video_title, video_description, video_name, shorts)
    if not video_added:
        print('Error: trying again...')
        return upload_single_video(channel, title_id, video_title, video_description, video_name, publish_time, shorts)
    youtube.handle_schedule(publish_time, shorts)

def next_datetime_to_schedule(last_datetime_str, allowed_times, shorts=False, shorts_number=None):
    last_datetime = datetime.strptime(last_datetime_str, "%Y-%m-%d %H:%M:%S")

    if shorts:
        if int(shorts_number) == 1:
            return last_datetime.strftime("%Y-%m-%d %H:%M:%S")
        next_datetime = last_datetime + timedelta(hours=1)
        return next_datetime.strftime("%Y-%m-%d %H:%M:%S")

    allowed_times.sort()
    last_time_str = last_datetime.strftime("%H:%M:%S")
    
    next_time_str = None
    for time_slot in allowed_times:
        if time_slot > last_time_str:
            next_time_str = time_slot
            break
            
    if next_time_str:
        next_date = last_datetime.date()
        next_time = datetime.strptime(next_time_str, "%H:%M:%S").time()
        next_datetime = datetime.combine(next_date, next_time)
    else:
        next_date = last_datetime.date() + timedelta(days=1)
        first_allowed_time_str = allowed_times[0]
        first_time = datetime.strptime(first_allowed_time_str, "%H:%M:%S").time()
        next_datetime = datetime.combine(next_date, first_time)
        
    return next_datetime.strftime("%Y-%m-%d %H:%M:%S")


def handle_upload(channel, video_title, video_description, title_id, is_shorts=False, shorts_number=-1):
    channel_upload = database.get_item('channels_upload', channel['id'], column_to_compare='channel_id')
    if not channel_upload:
        channel_upload_data = {
            "channel_id": channel['id'],
            "last_video_uploaded": -1,
            "last_shorts_uploaded": -1,
            "last_datetime": '01/01/2000',
            "allowed_times": ['16:00'],
        }
        channel_upload = database.insert(channel_upload_data, 'channels_upload')


    old_title = title_id < channel_upload['last_video_uploaded']
    same_title = title_id == channel_upload['last_video_uploaded']
    old_shorts = not is_shorts or shorts_number <= channel_upload['last_shorts_uploaded']
    
    if old_title or (same_title and old_shorts):
        return 
    
    video_name = f"shorts_{shorts_number}.mp4" if is_shorts else f"video.mp4"
    publish_time = next_datetime_to_schedule(channel_upload['last_datetime'], channel_upload['allowed_times'], shorts=is_shorts, shorts_number=shorts_number)

    upload_single_video(channel, title_id, video_title, video_description, video_name, publish_time, is_shorts)
    
    channel_upload['last_video_uploaded'] = title_id
    channel_upload['last_datetime'] = publish_time
    channel_upload['last_shorts_uploaded'] = shorts_number if is_shorts else -1

    for key, value in channel_upload:
        database.update('channels_upload', channel_upload['id'], key, value)

def get_shorts(shorts_path):
    shorts = []
    if os.path.exists(shorts_path):
        for filename in os.listdir(shorts_path):
            if filename.endswith(".mp3"):
                shorts.append(filename.split('.')[0])
    shorts.sort()
    return shorts

def run(channel_id):   
    print("--- Uploading Videos ---\n")
    channel = database.get_item('channels', channel_id)

    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    for title in titles:
        video = database.get_item('videos', title['id'], column_to_compare='title_id')
        print(f"\t-({channel_id}/{title['title_nubmer']}) {title['title']}")

        video_title = title['title']
        video_description = video['description']
        handle_upload(channel, video_title, video_description, title['title_number'])
        
        all_shorts = database.get_data('shorts', video['id'], video['id'])
        if not all_shorts:
            return
        
        for shorts in all_shorts:
            shorts_idea = [idea for idea in video['shorts_ideas'] if idea["id"] == shorts['number']]
            handle_upload(channel, shorts_idea['main_title'][:100], shorts['description'], title['title_number'], is_shorts=True, shorts_number=shorts['number'])
