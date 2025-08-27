from supabase import create_client, Client
from config.keys import SUPABASE_ANON_KEY, SUPABASE_URL, SUPABASE_CONNECTION_URI
import shutil
import os
import subprocess
from datetime import datetime
import json
import scripts.utils.handle_text as handle_text

db: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

ALLOWED_IMAGES_EXTENSIONS = ['jpg', 'png', 'jpeg']

def backup():
    if not SUPABASE_CONNECTION_URI:
        print("Error: No SUPABASE_CONNECTION_URI found.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = f"storage/backups"
    os.makedirs(output_path, exist_ok=True)
    output_file = f"{output_path}/{timestamp}.sql"

    command = [
        'pg_dump',
        '--dbname', SUPABASE_CONNECTION_URI,
        '--file', output_file,
        '--clean',
        '--if-exists'
    ]

    try:
        print(f"Starting database backup to file: {output_file}")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Backup done!")
    except FileNotFoundError:
        print("Error: 'pg_dump' not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

def export(file_name: str, data: str|list|dict, format='txt', path='storage/') -> str:
    try:
        if path[-1] != '/':
            path += '/'
            
        os.makedirs(path, exist_ok=True)
        export_path = f"{path}{file_name}.{format}"
        with open(export_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                f.write(data)
        
        return export_path
    except Exception as e:
        print(f"Error exporting {file_name}: {e}")
        return None

def log(file_name: str, data: str|list|dict, format='txt'):
    export(file_name, data, format, path='storage/logs')

def has_file(file_path):
    return os.path.exists(file_path)

def remove_file(file_path):
    if has_file(file_path):
        shutil.rmtree(file_path)

def get_prompt_template(prompt_type, file_name, variables):
    response_data = (
        db.table('prompts_templates')
        .select("*")
        .eq('type', prompt_type)
        .eq('name', file_name)
        .execute()
        .data
    )

    if not response_data:
        raise ValueError(f"Nenhum template encontrado para type='{prompt_type}' e name='{file_name}'")
    
    prompt_template_obj = response_data[0]

    prompt_obj = handle_text.substitute_variables_in_json(prompt_template_obj, variables)

    final_prompt_string = json.dumps(prompt_obj['prompt'], indent=2, ensure_ascii=False)
    
    return final_prompt_string

def get_prompt_file(channel_id, prompt_type):
    prompt = get_item('prompts', channel_id, 'channel_id', select=prompt_type)

    return prompt

def update(table, id, column, value):
    data = (
        db.table(table)
        .update({column: value})
        .eq("id", id)
        .execute()
        .data
    )

    if data:
        return data[0][column]
    
    return None

def insert(data, table=''):     
    item = (
        db.table(table)
        .insert(data)
        .execute()
        .data
    )

    return item[0]

def get_item(table, value=None, column_to_compare='id', select="*"):
    item = (
        db.table(table)
        .select(select)
        .eq(column_to_compare, value)
        .execute()
        .data
    )
    
    if not item:
        return []

    if select != "*":
        return item[0][select]
    
    return item[0]

def get_all_data(table, select="*"):
    data = (
        db.table(table)
        .select(select)
        .execute()
        .data
    )

    return data

def get_data(table, value=None, column_to_compare='id',select="*"):
    query = db.table(table).select(select)
    if isinstance(value, list):
        query = query.in_(column_to_compare, value)
    elif value is not None:
        query = query.eq(column_to_compare, value)

    item = query.execute().data

    if select != "*" and isinstance(select, str) and not isinstance(value, list):
        return item[0][select] if item else None

    return item

def exists(table, value=None, column_to_compare='id'):
    items = (
        db.table(table)
        .select('id', count='exact', head=True)
        .eq(column_to_compare, value)
        .execute()
    )

    return items.count > 0

def channel_titles(channel_id):     
    titles = get_data('titles', channel_id, column_to_compare='channel_id')   
    sorted_titles = sorted(titles, key=lambda x: x["title_number"])

    return sorted_titles

def title_channel(title_id):     
    title = get_item('titles', title_id)
    channel = get_item('channels', title['channel_id'])

    return channel

def next_title_number(channel_id):
    titles = channel_titles(channel_id)
    
    if not titles:
        return 1

    highest_number = max(item['title_number'] for item in titles)
    return highest_number + 1

def channel_variables(channel_id):
    variables = get_item('channels_responses', channel_id, column_to_compare='channel_id', select='variables')
    return variables