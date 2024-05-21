import boto3
import json
import base64
from io import BytesIO
from pdf2image import convert_from_bytes
from PIL import Image
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
CLAUDE_CONFIG_BASE =  {
    'max_tokens': 100000,
    'temperature': 1,
    'anthropic_version': 'bedrock-2023-05-31',
    'top_p': 0.999,
    'stop_sequences': ['Human:']
}

def convert_pdf_to_images(pdf_loc):
    with open(f'{pdf_loc}', 'rb') as f:
        contents = f.read()
    return convert_from_bytes(contents)

def parse_response(response):
    r = json.loads(response['body'].read().decode('utf-8'))
    return r['content'][0]['text']

from tqdm import tqdm
def convert_image_to_bytes(img, max_size = (1200, 800)):
    # if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
    #     img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
    with BytesIO() as output:
        img.save(output, 'jpeg')
        return base64.b64encode(output.getvalue()).decode('utf-8')
    
def render_payload(images, prompt, system_prompt, claude_config = None):
    if claude_config is None:
        claude_config = CLAUDE_CONFIG_BASE
    content = [{"type": "image","source": {"type": "base64", "media_type": "image/jpeg", "data": encoded_jpg}} for encoded_jpg in images]
    
    content.append({
        "type": "text",
        "text": prompt
        })
    messages = {"role": "user", "content": content}
    system_prompt = "You are a data entry helper"
    return {'messages': [messages], **claude_config, "system": system_prompt}


def get_jinja_env(src = 'templates/'):
    
    return Environment(
        loader=FileSystemLoader(src),
        autoescape=select_autoescape()
    )