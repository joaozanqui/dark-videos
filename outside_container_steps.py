import scripts.images.main as generate_images
import scripts.audios.main as generate_audios
import scripts.upload.main as handle_upload

def images(channel_id):
    generate_images.run(channel_id)

def audios(channel_id):
    generate_audios.run(channel_id)

def upload(channel_id):
    handle_upload.run(channel_id)
