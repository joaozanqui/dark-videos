import scripts.channel_analysis.main as channel_analysis
import scripts.ideas.main as ideas

if __name__ == "__main__":
    # insights_p1, insights_p2, insights_p3 =  channel_analysis.run_full_analysis_pipeline()
    with open('storage/analysis/insights_p1.txt', "r", encoding="utf-8") as file:
        insights_p1 = file.read() 
    with open('storage/analysis/insights_p2.txt', "r", encoding="utf-8") as file:
        insights_p2 = file.read() 
    with open('storage/analysis/insights_p3.txt', "r", encoding="utf-8") as file:
        insights_p3 = file.read()      
        
    ideas.run(insights_p1, insights_p2, insights_p3)