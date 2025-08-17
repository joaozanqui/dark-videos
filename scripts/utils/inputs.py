import scripts.database as database

def yes_or_no(text):
    allowed_answers = ['y', 'n']
    yes_or_no = input(f"{text} (y/n)\n")
    
    while yes_or_no.lower() not in allowed_answers :
        yes_or_no = input("Please press 'Y' for YES or 'N' for 'NO'\n ->")
    
    return True if yes_or_no.lower() == 'y' else False 

def select_from_data(table):
    all_data = database.get_all_data(table)
    data_map = {item['id']: item for item in all_data}

    print(f"\n- Select one item from '{table}':")
    for id, data in data_map.items():
        name = data.get('channel_name') or data.get('name')
        if table == 'analysis':
            channels_with_this_analysis = database.get_data('channels', id, column_to_compare='analysis_id')
            print(f"{id} - {name} ({[channel['name'] for channel in channels_with_this_analysis]})")
        else:
            print(f"{id} - {name}")

    selected_data = None
    while not selected_data:
        try:
            action = int(input(f"\n- Select the ID -> "))
            selected_data = data_map[action]
        except (ValueError, KeyError):
            print("Invalid ID.")
            
    return selected_data