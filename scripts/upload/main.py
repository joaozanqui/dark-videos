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

def next_datetime_to_schedule(last_datetime_str, allowed_times, shorts=False, shorts_id=None):
    last_datetime = datetime.strptime(last_datetime_str, "%Y-%m-%d %H:%M:%S")

    if shorts:
        if int(shorts_id) == 1:
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


def handle_upload(channel, video_title, video_description, title_id, shorts=False, shorts_id=None):
    old_title = int(title_id) < int(channel['last_title_uploaded'])
    same_title = int(title_id) == int(channel['last_title_uploaded'])
    same_title_but_old_shorts = (same_title and (not shorts or int(shorts_id) <= int(channel['last_shorts_uploaded'])))

    if old_title or same_title_but_old_shorts:
        return 
    
    video_name = f"shorts_{shorts_id}.mp4" if shorts else f"video.mp4"
    publish_time = next_datetime_to_schedule(channel['last_datetime'], channel['allowed_times'], shorts=shorts, shorts_id=shorts_id)

    upload_single_video(channel, title_id, video_title, video_description, video_name, publish_time, shorts)
    
    channel['last_title_uploaded'] = int(title_id)
    channel['last_datetime'] = publish_time
    channel['last_shorts_uploaded'] = int(shorts_id) if shorts else -1

    database.update_channels(channel)

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
    channel = database.get_channel_by_id(channel_id)

    print(f"- {channel['name']}")
    titles = database.get_titles(channel_id)

    for title_id, title in enumerate(titles):
        final_path = f"storage/videos/{channel_id}/{title_id}"
        shorts_path = f"storage/shorts/{channel_id}/{title_id}"
        print(f"\t-({channel_id}/{title_id}) {title['title']}")

        video_infos = database.get_txt_data(f"{final_path}/infos.txt")
        if not video_infos:
            continue

        video_title, _, video_description = video_infos.partition('\n')
        handle_upload(channel, video_title, video_description, title_id)

        shorts = get_shorts(shorts_path)
        if not shorts:
            return
        for shorts_name in shorts:
            shorts_id = shorts_name.split('_')[1]
            description = database.get_txt_data(f"{final_path}/{shorts_name}_description.txt")
            handle_upload(channel, video_title, description, title_id, shorts=True, shorts_id=shorts_id)