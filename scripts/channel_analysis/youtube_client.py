from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import xml.etree.ElementTree as ET
from config.keys import GOOGLE_API_KEY
from googleapiclient.discovery import build, Resource  

def get_channel_id_from_url(youtube: Resource, channel_url: str) -> Optional[str]:
    if "/channel/" in channel_url:
        return channel_url.split("/channel/")[-1].split("/")[0]
    
    identifier = channel_url.split("/")[-1]
    if not identifier: 
        identifier = channel_url.split("/")[-2]

    try:
        search_response = youtube.channels().list(
            part="id",
            forUsername=identifier
        ).execute()
        if search_response.get("items"):
            return search_response["items"][0]["id"]

        search_response_general = youtube.search().list(
            part="snippet",
            q=identifier,
            type="channel",
            maxResults=1
        ).execute()
        if search_response_general.get("items"):
            found_channel_title = search_response_general["items"][0]["snippet"]["title"]
            print(f"Found channel '{found_channel_title}' via general search.")
            return search_response_general["items"][0]["snippet"]["channelId"]
            
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred while trying to get channel ID: {e.content}")
    except Exception as e:
        print(f"An error occurred while trying to get channel ID: {e}")
    
    print(f"Could not reliably determine channel ID for '{identifier}' from URL '{channel_url}'.")
    print("Please try providing a direct channel ID (e.g., UCK8sQmJBp8GCxrOtXWBpyEA) or ensure the custom URL/username is exact.")
    return None

def get_channel_details(youtube: Resource, channel_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = youtube.channels().list(
            part="snippet,contentDetails",
            id=channel_id
        ).execute()
        if not response.get("items"):
            print(f"No channel found with ID: {channel_id}")
            return None
        return response["items"][0]
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    except Exception as e:
        print(f"An error occurred in get_channel_details: {e}")
        return None

def get_videos_from_playlist(
    youtube: Resource,
    playlist_id: str,
    published_after_date_str: str
) -> List[Dict[str, Any]]:
    videos_basic_info: List[Dict[str, Any]] = []
    all_video_ids: List[str] = []
    next_page_token: Optional[str] = None
    published_after_dt = datetime.fromisoformat(published_after_date_str)

    while True:
        try:
            response = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred while fetching playlist items: {e.content}")
            break
        except Exception as e:
            print(f"An error occurred while fetching playlist items: {e}")
            break

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            video_published_at_str = snippet.get("publishedAt")

            if not video_id or not video_published_at_str:
                continue

            if video_published_at_str.endswith("Z"):
                video_published_at_dt = datetime.fromisoformat(video_published_at_str[:-1] + "+00:00")
            else:
                video_published_at_dt = datetime.fromisoformat(video_published_at_str)

            if video_published_at_dt >= published_after_dt:
                videos_basic_info.append({
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "PublishedAt": video_published_at_str,
                    "description": snippet.get("description")
                })
                all_video_ids.append(video_id)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    if not all_video_ids:
        return []
    
    viewcount_map: Dict[str, int] = {}
    for i in range(0, len(all_video_ids), 50):
        batch_ids = all_video_ids[i : i + 50]
        try:
            stats_response = youtube.videos().list(
                part="statistics",
                id=",".join(batch_ids)
            ).execute()
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred while fetching video statistics: {e.content}")
            continue
        except Exception as e:
            print(f"An error occurred while fetching video statistics: {e}")
            continue

        for vid_item in stats_response.get("items", []):
            vid_id = vid_item.get("id")
            stats = vid_item.get("statistics", {})
            viewcount_map[vid_id] = int(stats.get("viewCount", 0))

    for vid in videos_basic_info:
        vid_id = vid["video_id"]
        vid["viewCount"] = viewcount_map.get(vid_id, 0)

    videos_basic_info.sort(key=lambda v: v["PublishedAt"], reverse=True)

    return videos_basic_info

def get_youtube_service() -> Optional[Resource]:
    try:
        return build("youtube", "v3", developerKey=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return None

def get_youtube_channel_data(
    channel_url: str,
    years_ago: int = 3
) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    youtube_service = get_youtube_service()
    if not youtube_service:
        return None

    channel_id = None
    channel_id = get_channel_id_from_url(youtube_service, channel_url)

    if not channel_id:
        print(f"Failed to resolve channel ID for: {channel_url}")
        return None

    channel_data = get_channel_details(youtube_service, channel_id)

    if not channel_data:
        return None

    channel_name = channel_data.get("snippet", {}).get("title", "Unknown Channel")
    channel_description = channel_data.get("snippet", {}).get("description", "Unknown Description")
    uploads_playlist_id = channel_data.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

    if not uploads_playlist_id:
        print(f"Could not find uploads playlist ID for channel: {channel_name} ({channel_id})")
        return None


    n_years_ago_dt = datetime.now(timezone.utc) - timedelta(days=years_ago * 365.25)
    published_after_date_iso = n_years_ago_dt.isoformat()


    print(f"Fetching videos for channel '{channel_name}' (ID: {channel_id}) from playlist '{uploads_playlist_id}' published after {published_after_date_iso}...")
    
    videos = get_videos_from_playlist(youtube_service, uploads_playlist_id, published_after_date_iso)
    
    print(f"Found {len(videos)} videos published in the last {years_ago} years.")
    return channel_name, channel_description, videos

def fetch_top_liked_comments(
    video_id: str,
    max_comments_to_fetch: int = 100
) -> List[Dict[str, Any]]:
    youtube = get_youtube_service()
    comments = []
    next_page_token = None
    total_fetched = 0

    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50,
                order="relevance",
                pageToken=next_page_token,
                textFormat="plainText" 
            ).execute()
        except HttpError as e:
            print(f"HTTP error {e.resp.status} getting video comments {video_id}: {e.content}")
            break
        except Exception as e:
            print(f"Unexpecting error getting video comments {video_id}: {e}")
            break

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comment_id = item["snippet"]["topLevelComment"]["id"]
            text = snippet.get("textDisplay") or snippet.get("textOriginal")
            author = snippet.get("authorDisplayName")
            published_at = snippet.get("publishedAt")
            like_count = int(snippet.get("likeCount", 0))

            comments.append({
                "comment_id": comment_id,
                "author": author,
                "text": text,
                "publishedAt": published_at,
                "likeCount": like_count
            })
            total_fetched += 1

            if total_fetched >= max_comments_to_fetch:
                break

        if total_fetched >= max_comments_to_fetch:
            break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    order_comments = sorted(comments, key=lambda c: c["likeCount"], reverse=True)
    return order_comments

def get_transcripts(video_id: str, attempt_numer=1) -> str:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except TranscriptsDisabled:
        print("Transcripts Disabled")
        return ""
    except NoTranscriptFound:
        print("No Transcript Found")
        return ""
    except ET.ParseError:
        if attempt_numer < 5:
            return get_transcripts(video_id, attempt_numer=attempt_numer + 1)
        return "[Parsing Error: invalid or empty response]"
    except Exception as e:
        return f"[Error finding transcripts: {e}]"
    