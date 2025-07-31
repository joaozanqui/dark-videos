from typing import List, Dict, Any
import scripts.database as database

def generate_phase1_prompt(channel_name: str, channel_description: str, videos_data: List[Dict[str, Any]]) -> str:

    if not videos_data:
        data = "No video data provided or found for the last 3 years."
    else:
        limit = 300
        data = ''
        for video in videos_data[:limit]: 
            data += f"- Title: {video.get('title', 'N/A')}, ViewCount: {video.get('viewCount', 'N/A')}, Published: {video.get('published_at', 'N/A')}\n"
        if len(videos_data) > limit:
            data += f"... and {len(videos_data) - limit} more videos.\n"
    
    variables = {
        "channel_name": channel_name,
        "channel_description": channel_description,
        "data": videos_data
    }

    return database.build_prompt('analysis', 'phase1-channel-analysis', variables)


def generate_phase2_prompt(comments_text: str) -> str:
    variables = {
        "comments_text": comments_text
    }

    return database.build_prompt('analysis', 'phase2-comments-analysis', variables)
    
def generate_phase3_prompt(transcript_text: str, video_title: str) -> str:
    variables = {
        "transcript_text": transcript_text,
        "video_title": video_title
    }

    return database.build_prompt('analysis', 'phase3-transcripts-analysis', variables)

def generate_phase3_merge_prompt(analysis: str, videos_qty: int, channel_name: str) -> str:
    variables = {
        "analysis": analysis,
        "videos_qty": videos_qty,
        "channel_name": channel_name
    }

    return database.build_prompt('analysis', 'phase3-merge-prompts', variables)
