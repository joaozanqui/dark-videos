from titles_ideas.utils import (
    get_titles_language,
    get_youtube_channel_url
)

from titles_ideas.youtube_client import (
    get_youtube_channel_data, 
    fetch_top_liked_comments,
    get_transcripts
)

from titles_ideas.gemini_analyzer import (
    generate_phase1_prompt,
    generate_phase2_prompt,
    generate_phase3_prompt,
    generate_phase3_merge_prompt,
    generate_phase4_prompt
)

from utils import (
    get_gemini_model,
    analyze_with_gemini,
    export
)

def titles_generation(insights_p1, insights_p2, insights_p3, channel_name, model):
    language = get_titles_language()
    prompt_p4 = generate_phase4_prompt(insights_p1, insights_p2, insights_p3, channel_name, language)   
    title_ideas = analyze_with_gemini(prompt_p4, model)
    
    if not title_ideas:
        print("Failed to generate title ideas from Phase 4.")
        return None

    print("\nGenerated Viral Video Title Ideas (for your new agent/scripts):")
    title_ideas_path = export('title_ideas', title_ideas, path='storage/titles/')
    print(f"Title Ideas of Phase 4 saved at {title_ideas_path}")
    
    return title_ideas

def transcripts_analysis(most_viewed_videos, channel_name, model):
    most_viewed_videos_qty = 20
    videos = most_viewed_videos[:most_viewed_videos_qty]
    analysis = ''
    
    for video in videos:
        transcripts = get_transcripts(video['video_id'])
        prompt_p3 = generate_phase3_prompt(transcripts, video['title'])
        analysis += analyze_with_gemini(prompt_p3, model)
        analysis += "\n"
    
    prompt_p3 = generate_phase3_merge_prompt(analysis, most_viewed_videos_qty, channel_name)
    insights_p3 = analyze_with_gemini(prompt_p3, model)
    
    if not insights_p3:
        print("Failed to get insights from Phase 3.")
        return None
    
    insights_p3_path = export('insights_p3', insights_p3, path='storage/titles/')
    print(f"Insights of Phase 3 (Transcripts Analysis) saved at {insights_p3_path}")
    
    return insights_p3
    
def comments_analysis(most_viewed_videos, model):    
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
    insights_p2 = analyze_with_gemini(prompt_p2, model)
    
    if not insights_p2:
        print("Failed to get insights from Phase 2.")
        return None
    
    insights_p2_path = export('insights_p2', insights_p2, path='storage/titles/')
    print(f"Insights of Phase 2 (Comments Analysis) saved at {insights_p2_path}")
    
    return insights_p2
    
def channel_analysis(channel_name, channel_description, videos_list, model):    
    prompt_p1 = generate_phase1_prompt(channel_name, channel_description, videos_list)
    insights_p1 = analyze_with_gemini(prompt_p1, model)
    
    if not insights_p1:
        print("Failed to get insights from Phase 1.")
        return None
    
    insights_p1_path = export('insights_p1', insights_p1, path='storage/titles/')
    print(f"Insights of Phase 1 (Video Data Analysis) saved at {insights_p1_path}")
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

def run_full_analysis_pipeline():
    gemini_model = get_gemini_model()
    
    print("\n--- Step 1: Fetching YouTube Channel Data ---")
    channel_url = get_youtube_channel_url()
    youtube_data = get_channel_data(channel_url)
    channel_name, channel_description, videos_list = youtube_data
    most_viewed_videos = sorted(videos_list, key=lambda x: x["viewCount"], reverse=True)
    
    print("\n--- Phase 1: Initial Channel Analysis (using Gemini) ---")
    insights_p1 = channel_analysis(channel_name, channel_description, videos_list, gemini_model)
    
    print("\n--- Phase 2: Comment Analysis (using Gemini) ---")
    insights_p2 = comments_analysis(most_viewed_videos, gemini_model)

    print("\n--- Phase 3: Transcript Analysis (using Gemini) ---")
    insights_p3 = transcripts_analysis(most_viewed_videos, channel_name, gemini_model)

    if insights_p1 and insights_p2 and insights_p3:
        print("\n--- Phase 4: Generating Viral Video Title Ideas (using Gemini) ---")
        titles_ideas = titles_generation(insights_p1, insights_p2, insights_p3, channel_name, gemini_model)
    else:
        print("\nSkipping Phase 4 as not all preceding insights are available.")

    print("\n--- Analysis Pipeline Complete ---")
    return titles_ideas
