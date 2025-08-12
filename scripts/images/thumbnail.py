from PIL import ImageFont, ImageDraw, Image
import textwrap
import os 
import scripts.database as database
from scripts.images.main import ALLOWED_IMAGES_EXTENSIONS

FONT_PATH = "assets/font.ttf"

def handle_text(text: str, text_area_width: int, text_area_height: int):
    font_size = 150
    font = None
    wrapped_text = ""
    
    max_vertical_size = text_area_height * 0.25
    
    temp_img = Image.new('RGB', (text_area_width, text_area_height))
    draw = ImageDraw.Draw(temp_img)

    while font_size > 10:
        font = ImageFont.truetype(FONT_PATH, font_size)
        
        avg_char_width = font.getlength('W')
        max_chars = int(text_area_width / avg_char_width) if avg_char_width > 0 else 1
        wrapped_text = textwrap.fill(text, width=max_chars if max_chars > 0 else 1)
        
        _, _, text_w, text_h = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=15)
        
        if text_w < text_area_width and text_h < text_area_height and text_h <= max_vertical_size:
            break
        
        font_size -= 2

    return wrapped_text, font

def draw_thumbnail(background: Image.Image, expression: str, wrapped_text: str, font: ImageFont.ImageFont, channel_id: str):
    width, height = background.size

    try:
        expression_path = f"assets/expressions/{channel_id}/transparent/{expression}.png"
        if not os.path.exists(expression_path):
            expression_path = f"assets/expressions/{channel_id}/transparent/serious.png"

        expression_img = Image.open(expression_path).convert("RGBA")
        img_max_height = int(height * 1.2)
        expression_img.thumbnail((img_max_height, img_max_height))
        img_x = (width // 4) - (expression_img.width // 2)
        img_y = (height // 2) - (expression_img.height // 2)
        background.paste(expression_img, (img_x, img_y), expression_img)
    except FileNotFoundError:
        print(f"\t\t-Warning: Expression Image '{expression_path}' not found.")
    except Exception as e:
        print(f"\t\t-Error processing expression image: {e}")

    draw = ImageDraw.Draw(background)
    
    right_quadrant_x_start = width // 2
    text_area_width = width // 2
    
    _, _, text_width, text_height = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=15)
    
    text_x = right_quadrant_x_start + (text_area_width - text_width) // 2
    text_y = (height - text_height) // 2

    draw.multiline_text(
        (text_x, text_y),
        wrapped_text,
        font=font,
        fill=(255, 255, 0), 
        stroke_width=4, 
        stroke_fill=(0, 0, 0), 
        align="center",
        spacing=10
    )

    return background

def image_file_path(final_path):
    image_path = ''
    for ext in ALLOWED_IMAGES_EXTENSIONS:
        image_path = f"{final_path}/image.{ext}"
        has_image = os.path.exists(image_path)
        if has_image:
            return image_path
        
    print(f"\t\t-No image file")
    return ''    

def build(image_path: str, output_path: str, channel_id: str, thumbnail_data: dict):
    try:
        print(f"\t\t-Creating Thumbnail...")
        background = Image.open(image_path).convert("RGBA")
        width, height = background.size

        text_area_width = int((width*0.75) * 0.9)
        text_area_height = int(height * 0.9)
        
        wrapped_text, font = handle_text(
            thumbnail_data['phrase'].upper(),
            text_area_width,
            text_area_height
        )

        thumbnail_image = draw_thumbnail(
            background, 
            thumbnail_data['expression'],
            wrapped_text,
            font,
            channel_id
        )

        thumbnail_image.save(output_path)
        print(f"\t\t-Thumbnail created successfully!")

        return True

    except FileNotFoundError as fnfe:
        print(f"Error thumbnail image not found: {fnfe}")
        return False
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

def run(channel_id):
    channel = database.get_item('channels', channel_id)
    print(f"- {channel['name']}")
    titles = database.channel_titles(channel_id)

    for title in titles:
        print(f"\t- {title['title_number']}. {title['title']}")
        final_path = f"storage/{channel_id}/{title['title_number']}"

        video = database.get_item('videos', title['id'], column_to_compare='title_id')
        if video['has_thumbnail']:
            continue

        if video['has_image']:
            image_path = image_file_path(final_path)
            output_thumbnail_path = f"{final_path}/thumbnail.png"
            if build(image_path, output_thumbnail_path, channel_id, video['thumbnail_data']):
                database.update('videos', video['id'], 'has_thumbnail', True)
