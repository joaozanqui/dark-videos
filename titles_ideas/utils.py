import json
from typing import Optional
from googleapiclient.discovery import build, Resource  
from config import GOOGLE_API_KEY

def get_youtube_channel_url():
    with open('data.json', "r", encoding="utf-8") as file:
        data = json.load(file)    
    channel_url_or_id = data['url']

    if not channel_url_or_id:
        print("No channel URL or ID provided. Exiting.")
        return None

    return channel_url_or_id

def get_titles_language():
    with open('data.json', "r", encoding="utf-8") as file:
        data = json.load(file)    
    language = data['titles_language']

    if not language:
        language = 'english'

    return language

def get_youtube_service() -> Optional[Resource]:
    try:
        return build("youtube", "v3", developerKey=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return None