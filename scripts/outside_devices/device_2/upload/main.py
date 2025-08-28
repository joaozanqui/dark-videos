import scripts.outside_devices.device_2.utils as utils
import scripts.outside_devices.device_2.upload.youtube as youtube
from config.keys import DEVICE
import scripts.database as database

def run(channel, title_number, video_title, video_description, file_name, publish_time, shorts):
    device_infos = database.get_item('devices', DEVICE)
    file_path = f"{device_infos['final_path']}/storage/{channel['id']}/{title_number}"

    utils.goto_page(page=channel['upload_url'])
    video_added = youtube.add_video(file_path, video_title, video_description, file_name, shorts)
    if not video_added:
        print('Error: trying again...')
        return run()
    youtube.handle_schedule(publish_time, shorts)