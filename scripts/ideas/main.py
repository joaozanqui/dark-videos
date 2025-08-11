
import scripts.ideas.new_channel as new_channel 
import scripts.utils.gemini as gemini
import scripts.utils.inputs as inputs
import scripts.database as database

def get_channel_info_prompt(channel, analysis, step):
    file_name = f"channel-{step}"
    language = database.get_item('languages', channel['language_id'])

    variables = {
        "CHANNEL": channel,
        "INSIGHTS_P1": analysis['insights_p1'],
        "INSIGHTS_P2": analysis['insights_p2'],
        "language": language['name']
    }
    
    prompt = database.get_prompt_template('ideas', file_name, variables)    
    response = gemini.run(prompt_json=prompt)
        
    return response

def generate_channels(analysis):
    confirm = False
    while not confirm:
        new_channels = new_channel.run(analysis)
        print("\n- Channels:\n")
        
        for i, channel in enumerate(new_channels, 1):
            print(f"  --- Channel {i} ---")
            for key, value in channel.items():
                formatted_key = key.replace('_', ' ').title()
                print(f"    {formatted_key}: {value}")
            print()

        confirm = inputs.yes_or_no("Confirm the channels?")
        
    return new_channels

def run(analysis):
    if not analysis['insights_p1'] or not analysis['insights_p2'] or not analysis['insights_p3']:
        print("\nSkipping as not all preceding insights are available.")
        return {}
    
    print("\n--- Generating Viral Channel and Videos Ideas (using Gemini) ---")
    channels = generate_channels(analysis)
    added_channels = []
    for channel in channels:
        added_channels.append(database.insert(channel, 'channels'))

    print(f"New channels ideas saved!")

    for channel in added_channels:
        channel_data = {
            "channel_id": channel['id']
        }
        
        for step in ["logo", "profile", "banner", "description"]:
            print(f"- Generating {step}...")
            channel_data[step] = get_channel_info_prompt(channel, analysis, step=step)

        database.insert(channel_data, 'channels_responses')