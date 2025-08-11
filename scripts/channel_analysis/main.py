from scripts.channel_analysis.youtube_client import (
    get_youtube_channel_data, 
    fetch_top_liked_comments,
    get_transcripts
)

from scripts.channel_analysis.gemini_analyzer import (
    generate_phase1_prompt,
    generate_phase2_prompt,
    generate_phase3_prompt,
    generate_phase3_merge_prompt,
)

import scripts.utils.gemini as gemini
import scripts.database as database

def transcripts_analysis(most_viewed_videos, channel_name):
    most_viewed_videos_qty = 20
    videos = most_viewed_videos[:most_viewed_videos_qty]
    analysis = ''
    
    for video in videos:
        transcripts = get_transcripts(video['video_id'])
        prompt_p3 = generate_phase3_prompt(transcripts, video['title'])
        analysis += gemini.run(prompt_json=prompt_p3)
        analysis += "\n"
    
    prompt_p3 = generate_phase3_merge_prompt(analysis, most_viewed_videos_qty, channel_name)
    insights_p3 = gemini.run(prompt_json=prompt_p3)
    
    if not insights_p3:
        print("Failed to get insights from Phase 3.")
        return None
    
    print(f"Insights of Phase 3 (Transcripts Analysis) done!")    
    return insights_p3
    
def comments_analysis(most_viewed_videos):    
    most_viewed_videos_qty = 20
    videos = most_viewed_videos[:most_viewed_videos_qty]
       
    max_comments_to_fetch = 100
    comments_text = ''
        
    for video in videos:
        comments = fetch_top_liked_comments(video['video_id'], max_comments_to_fetch)
        comments_text += f"Video: {video['title']}\n{max_comments_to_fetch} most popular comments:\n"
        for comment in comments:
            comments_text += f"(Like Count: {comment['likeCount']}) - {comment['text']}\n"
        comments_text += "\n"    
        
    prompt_p2 = generate_phase2_prompt(comments_text)
    insights_p2 = gemini.run(prompt_json=prompt_p2)
    
    if not insights_p2:
        print("Failed to get insights from Phase 2.")
        return None
    
    print(f"Insights of Phase 2 (Comments Analysis) done!")    
    return insights_p2
    
def channel_analysis(channel_name, channel_description, videos_list):    
    prompt_p1 = generate_phase1_prompt(channel_name, channel_description, videos_list)
    insights_p1 = gemini.run(prompt_json=prompt_p1)
    
    if not insights_p1:
        print("Failed to get insights from Phase 1.")
        return None
    
    print(f"Insights of Phase 1 (Video Data Analysis) done!")
    return insights_p1

def get_channel_data(channel_url):
    years_ago = 3
    youtube_data = get_youtube_channel_data(channel_url, years_ago=years_ago)

    if not youtube_data:
        print("Failed to retrieve YouTube channel data. Exiting.")
        return None

    channel_name, channel_description, videos_list = youtube_data

    print(f"Successfully fetched data for channel: {channel_name}")
    print(f"Found {len(videos_list)} videos from the last {years_ago} years.")

    if not videos_list:
        print("No videos found for this channel in the specified period. Analysis might be limited.")
    
    return youtube_data        

def select_channel():
    channel_url = input("Paste the CHANNEL URL here.\n -> ")
    return channel_url

def run_full_analysis_pipeline():
    print("\n--- Step 1: Fetching YouTube Channel Data ---")
    channel_url = select_channel()
    youtube_data = get_channel_data(channel_url)
    channel_name, channel_description, videos_list = youtube_data
    most_viewed_videos = sorted(videos_list, key=lambda x: x["viewCount"], reverse=True)
    
    print("\n--- Phase 1: Initial Channel Analysis (using Gemini) ---")
    insights_p1 = channel_analysis(channel_name, channel_description, videos_list)
    
    print("\n--- Phase 2: Comment Analysis (using Gemini) ---")
    insights_p2 = comments_analysis(most_viewed_videos)

    print("\n--- Phase 3: Transcript Analysis (using Gemini) ---")
    insights_p3 = transcripts_analysis(most_viewed_videos, channel_name)

    data = {
        "channel_name": channel_name,
        "channel_url": channel_url,
        "insights_p1": insights_p1,
        "insights_p2": insights_p2,
        "insights_p3": insights_p3
    }

    database.insert(data, 'analysis')

    return [insights_p1, insights_p2, insights_p3]