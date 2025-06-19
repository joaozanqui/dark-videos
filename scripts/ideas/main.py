
import scripts.ideas.new_channel as new_channel 
import scripts.ideas.titles as titles
from scripts.utils import get_gemini_model
import json

def run(insights_p1, insights_p2, insights_p3):
    gemini_model = get_gemini_model()

    if insights_p1 and insights_p2 and insights_p3:
        print("\n--- Generating Viral Videos Ideas (using Gemini) ---")
        # channels = new_channel.run(insights_p1, insights_p2, insights_p3, gemini_model)
        with open('storage/ideas/channels.json', "r", encoding="utf-8") as file:
            channels = json.load(file) 

        for i, channel in enumerate(channels):
            titles_ideas = titles.run(insights_p1, insights_p2, insights_p3, channel, i, gemini_model)
    else:
        print("\nSkipping as not all preceding insights are available.")
