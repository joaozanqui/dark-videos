import os

def get_allowed_expressions(channel_id, is_video=False):
    path = f"assets/expressions/{str(channel_id)}/{'chroma' if is_video else 'transparent'}"
    allowed_expressions = []
    for expression in os.listdir(path):
        full_path = os.path.join(path, expression)
        if os.path.isfile(full_path):
            allowed_expressions.append(expression.split('.')[0])
    
    return allowed_expressions