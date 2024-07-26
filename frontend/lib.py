import boto3
import json
import base64
from PIL import Image
from io import BytesIO
from random import randint


def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io


def get_base64_from_bytes(image_bytes):
    resized_io = get_bytesio_from_bytes(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str


def get_image_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    image = Image.open(image_io)
    return image
    

def get_png_base64(image):
    png_io = BytesIO()
    image.save(png_io, format="PNG")
    img_str = base64.b64encode(png_io.getvalue()).decode("utf-8")
    return img_str


#load the bytes from a file on disk
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes


def get_claude_response_text(response):

    response = json.loads(response.get('body').read())

    return response['content'][0]['text']


def get_claude_mask_prompt_request_body(mask_prompt):
    system_prompt = """
    If the input language is in English, respond with the exact same input and only the exact same input. Do not add or remove any words.
    If the input langugae is NOT in English, translate the input to English and return only the translated response. Do not add or remove any words after translation.
    """
    user_message = {"role": "user", "content": mask_prompt}
    assistant_message =  {"role": "assistant", "content": ""}
    messages = [user_message, assistant_message]
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": messages
    }

    return json.dumps(body)


def get_claude_prompt_content_request_body(prompt_content):
    system_prompt = """
    If the input language is in English, respond with the exact same input and only the exact same input. Do not add or remove any words.
    If the input langugae is NOT in English, translate the input to English and return only the translated response. Do not add or remove any words after translation.
    """
    user_message = {"role": "user", "content": prompt_content}
    assistant_message =  {"role": "assistant", "content": ""}
    messages = [user_message, assistant_message]
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": messages
    }

    return json.dumps(body)


def get_titan_image_masking_request_body(prompt_content, image_bytes, painting_mode, masking_mode, mask_bytes, mask_prompt):
    
    original_image = get_image_from_bytes(image_bytes)
    
    target_width, target_height = original_image.size
    
    image_base64 = get_base64_from_bytes(image_bytes)
    
    mask_base64 = get_base64_from_bytes(mask_bytes)
    
    body = {
        "taskType": painting_mode,
        "imageGenerationConfig": {
            "numberOfImages": 5,  # Number of variations to generate
            "quality": "premium",  # Allowed values are "standard" and "premium"
            "height": target_height,
            "width": target_width,
            "cfgScale": 8.0,
            "seed": randint(0, 100000),  # Use a random seed
        },
    }
    
    params = {
        "image": image_base64,
        "text": prompt_content,  # What should be displayed in the final image
    }
    
    if masking_mode == 'Image':
        params['maskImage'] = mask_base64
    else:
        params['maskPrompt'] = mask_prompt
        
    
    if painting_mode == 'OUTPAINTING':
        params['outPaintingMode'] = 'DEFAULT'
        body['outPaintingParams'] = params
    else:
        body['inPaintingParams'] = params
    
    return json.dumps(body)


def get_titan_response_image(response):

    response = json.loads(response.get('body').read())
    
    images = response.get('images')
    
    image_data_list = []
    for image in images:
        image_data = base64.b64decode(image)
        image_data_list.append(BytesIO(image_data))

    # image_data = base64.b64decode(images[0])

    # return BytesIO(image_data)
    return image_data_list


def get_image_from_model(prompt_content, image_bytes, painting_mode, masking_mode, mask_bytes=None, mask_prompt=None):
    session = boto3.Session()
    
    bedrock = session.client(service_name='bedrock-runtime') #creates a Bedrock client

    mask_prompt_request_body = get_claude_mask_prompt_request_body(mask_prompt)
    prompt_content_request_body = get_claude_prompt_content_request_body(prompt_content)

    mask_prompt_response = bedrock.invoke_model(body=mask_prompt_request_body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")
    prompt_content_response = bedrock.invoke_model(body=prompt_content_request_body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")

    translated_mask_prompt = get_claude_response_text(mask_prompt_response)
    translated_prompt_content = get_claude_response_text(prompt_content_response)
    
    image_request_body = get_titan_image_masking_request_body(translated_prompt_content, image_bytes, painting_mode, masking_mode, mask_bytes, translated_mask_prompt)
    
    response = bedrock.invoke_model(body=image_request_body, modelId="amazon.titan-image-generator-v1", contentType="application/json", accept="application/json")
    
    output = get_titan_response_image(response)
    
    return output

