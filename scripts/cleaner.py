import scripts.database as database

def run():
    final_path = "storage"
    channels = database.get_all_data('channels')
    for channel in channels:
        channel_path = f"{final_path}/{channel['id']}"
        if not database.has_file(channel_path):
            continue

        titles = database.channel_titles(channel['id'])
        for title in titles:
            title_path = f"{channel_path}/{title['title_number']}"
            if not database.has_file(title_path):
                continue

            video = database.get_item('videos', title['id'], 'title_id')
            if video['uploaded']:
                database.remove_file(title_path)