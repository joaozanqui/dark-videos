from typing import List, Dict, Any

def generate_phase1_prompt(channel_name: str, channel_description: str, videos_data: List[Dict[str, Any]]) -> str:
    prompt = f"YouTube Channel Analysis for Content Strategy: '{channel_name}'\n\n"
    prompt += "Channel description:\n"
    prompt += f"{channel_description}\n\n"
    prompt += "I am analyzing this channel to understand its success and get direction for my own channel in a similar niche.\n\n"
    prompt += "Recent Video Data (titles and publication dates from the last 3 years):\n"
    if not videos_data:
        prompt += "No video data provided or found for the last 3 years.\n"
    else:
        limit = 300
        for video in videos_data[:limit]: 
            prompt += f"- Title: {video.get('title', 'N/A')}, ViewCount: {video.get('viewCount', 'N/A')}, Published: {video.get('published_at', 'N/A')}\n"
        if len(videos_data) > limit:
            prompt += f"... and {len(videos_data) - limit} more videos.\n"
    
    prompt += "\nBased on this video data (especially titles and their view count), please help with the following:\n"
    prompt += "1. What are the recurring themes, topics, or content pillars evident from the video titles?\n"
    prompt += "2. Based *only* on the provided video titles and their view count, what might be the 'secret to success' or core appeal of this channel?\n"
    prompt += "3. What initial directions or content ideas would you suggest for a new channel in the same niche, focusing on leveraging insights from these video titles?\n"
    prompt += "4. Are there any apparent trends in topics over time, judging by the titles and their publication dates (if you can infer general periods like older vs. newer)?\n"
    prompt += "5. Based on the number of views count, is there a rule for titles that are most likely to go viral on YouTube in the same niche of the channel?\n"
    prompt += "Provide a concise analysis."
    return prompt

def generate_phase2_prompt(comments_text: str) -> str:
    prompt = f"YouTube Comment Analysis for Audience Insights:\n\n"
    prompt += "I've collected comments from popular videos of a target channel. Please analyze them.\n\n"
    prompt += "Collected Comments:\n"
    prompt += f'"""\n{comments_text}\n"""\n\n'
    prompt += "Based on these comments, please identify:\n"
    prompt += "1. Recurring themes, questions, or pain points mentioned by the audience.\n"
    prompt += "2. Positive sentiments: What do people praise or love about the content/channel?\n"
    prompt += "3. Negative sentiments or constructive criticism: What are the common complaints or areas for improvement?\n"
    prompt += "4. Unmet needs or desires: Are there suggestions for new content, formats, or topics?\n"
    prompt += "5. What valuable insights can be extracted to create highly engaging new videos that address the audience's core interests and concerns?\n"
    prompt += "Provide a concise analysis."
    return prompt

def generate_phase3_prompt(transcript_text: str, video_title: str) -> str:
    prompt = f"Detailed YouTube Video Transcript Analysis: '{video_title}'\n\n"
    prompt += "I am analyzing this video transcript to understand why it resonated with viewers.\n\n"
    prompt += "Video Transcript:\n"
    prompt += f'"""\n{transcript_text}\n"""\n\n'
    prompt += "Please provide a meticulous analysis focusing on:\n"
    prompt += "1. Script Structure: Introduction, development of ideas, main points, conclusion, calls to action (CTAs).\n"
    prompt += "2. Storytelling & Engagement: Hooks, narrative techniques, use of examples, emotional connection, pacing.\n"
    prompt += "3. Language & Tone: Style of communication (e.g., formal, informal, humorous, didactic), clarity, and rapport with the audience.\n"
    prompt += "4. Key Elements of Success: What specific aspects of this transcript likely contributed most to the video's popularity and impact?\n"
    prompt += "5. Actionable Learnings: What lessons can be applied to scripting new videos for similar success?\n"
    prompt += "Provide a concise analysis."
    return prompt

def generate_phase3_merge_prompt(analysis: str, videos_qty: int, channel_name: str) -> str:
    prompt = f"You are provided with a series of individual analyses, each corresponding to one of the {videos_qty} most-viewed videos from the YouTube channel '{channel_name}'. Each original analysis was generated from the video's transcript and focused on the following five aspects:\n"
    prompt += "1.  **Script Structure:** Introduction, development of ideas, main points, conclusion, calls to action (CTAs).\n"
    prompt += "2.  **Storytelling & Engagement:** Hooks, narrative techniques, use of examples, emotional connection, pacing.\n"
    prompt += "3.  **Language & Tone:** Style of communication (e.g., formal, informal, humorous, didactic), clarity, and rapport with the audience.\n"
    prompt += "4.  **Key Elements of Success:** Specific aspects of the transcript that likely contributed most to the video's popularity and impact.\n"
    prompt += "5.  **Actionable Learnings:** Lessons that can be applied to scripting new videos for similar success.\n"
    prompt += f"Here are the compiled individual analyses:\n{analysis}\n\n"
    prompt += "Your mission is to synthesize these individual analyses into a single, consolidated overview. Your goal is to identify overarching strategies observed across all the provided analyses.\n"
    prompt += "Please structure your consolidated analysis based on the same five points:\n"
    prompt += "1.  **Overall Script Structure Patterns:** What are the common approaches to introductions, idea development, main points, conclusions, and CTAs across the analyzed videos?\n"
    prompt += "2.  **Common Storytelling & Engagement Techniques:** What recurring hooks, narrative methods, uses of examples, emotional connection strategies, and pacing characteristics are prevalent?\n"
    prompt += "3.  **Predominant Language & Tone:** What is the general style of communication, level of clarity, and typical way of building rapport with the audience observed across the videos?\n"
    prompt += "4.  **Consolidated Key Elements of Success:** Based on all analyses, what are the most frequently cited or impactful elements contributing to the videos' popularity?\n"
    prompt += "5.  **Aggregated Actionable Learnings:** What are the most common and valuable lessons that can be applied to scripting new successful videos for this channel?\n"
    prompt += "Provide a concise yet comprehensive summary that captures the general trends and shared characteristics. Focus on what is commonly effective across the analyzed videos.\n"   
    
    return prompt

def generate_phase4_prompt(
    phase1_insights: str,
    phase2_insights: str,
    phase3_insights: str,
    target_channel_name: str,
    language: str
) -> str:
    json_format_response = f'''[{{"title": "title in {language}", "rationale": "explanation text"}}]'''
    
    prompt = f"Viral YouTube Title Generation (Inspired by '{target_channel_name}')\n\n"
    prompt += "Objective: Generate compelling video title ideas that can serve as prompts for an AI scriptwriter. These titles should be based on previous analyses of a successful channel and its audience.\n\n"
    prompt += "Summary of Insights from Phase 1 (Channel Video Data Analysis):\n"
    prompt += f'"""\n{phase1_insights}\n"""\n\n'
    prompt += "Summary of Insights from Phase 2 (Audience Comment Analysis):\n"
    prompt += f'"""\n{phase2_insights}\n"""\n\n'
    prompt += "Summary of Insights from Phase 3 (Successful Videos Transcript Analysis):\n"
    prompt += f'"""\n{phase3_insights}\n"""\n\n'
    prompt += "Task: Generate a list of at least 15-20 diverse video title ideas. These titles should:\n"
    prompt += "1. Be highly clickable and intriguing (clickbait).\n"
    prompt += "2. Reflect the successful themes, audience pain points, and narrative styles identified in the insights.\n"
    prompt += "3. Be formulated as clear directives or core concepts that an AI scriptwriting agent can easily understand and expand into a full script (e.g., 'The Ultimate Guide to X They Don't Want You to Know', 'I Tried Y for 7 Days & THIS Happened!', 'Stop Making These Z Mistakes Now').\n"
    prompt += "4. Vary in format (e.g., questions, numbered lists, bold claims, secrets revealed).\n"
    prompt += "5. Be suitable for the niche of the analyzed channel ('{target_channel_name}').\n"
    prompt += f""" Return a **JSON list of dictionaries**. Each dictionary must contain:
    ```json
    {json_format_response}
    ```"""
    prompt += f"\nDo **not include any explanatory text** — only the JSON output\n"
    
    return prompt

