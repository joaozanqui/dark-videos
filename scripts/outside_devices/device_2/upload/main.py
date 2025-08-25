import scripts.outside_devices.device_2.utils as utils
import scripts.outside_devices.device_2.upload.youtube as youtube

def run(channel, title_id, video_title, video_description, video_name, publish_time, shorts):
    utils.goto_page(page=channel['upload_url'])
    video_added = youtube.add_video(channel['id'], title_id, video_title, video_description, video_name, shorts)
    if not video_added:
        print('Error: trying again...')
        return run(channel, title_id, video_title, video_description, video_name, publish_time, shorts)
    youtube.handle_schedule(publish_time, shorts)