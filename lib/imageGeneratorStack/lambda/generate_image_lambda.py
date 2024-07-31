import json
import boto3
import base64
from PIL import Image
from io import BytesIO
from random import randint
import time
import uuid

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Check if the request is health check
    if event.get('httpMethod') == 'GET' and event.get('path') == '/health':
        return health_check()

    # Parse input from the event
    body = json.loads(event['body'])
    prompt_content = body['prompt_content']
    s3_bucket_name = body['s3_bucket_name']
    image_url = body['image_url']
    painting_mode = body['painting_mode']
    masking_mode = body['masking_mode']
    mask_prompt = body['mask_prompt'] if 'mask_prompt' in body else None
    num_output_images = body['num_output_images']
    print("Lambda invoked with painting mode..", painting_mode)

    image_bytes = download_from_s3(image_url)

    # Process the image
    result = get_image_from_model(prompt_content, image_bytes, painting_mode, masking_mode, mask_prompt, num_output_images)
    
    # Prepare the response
    output_image_urls = upload_images_to_s3(result[0], s3_bucket_name)

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'image_urls': output_image_urls,
            'translated_mask_prompt': result[1],
            'translated_prompt_content': result[2]
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    }
    
    return response

def download_from_s3(s3_url):
    bucket_name = s3_url.split('/')[2]
    key = '/'.join(s3_url.split('/')[3:])
    response = s3.get_object(Bucket=bucket_name, Key=key)
    return response['Body'].read()

def upload_images_to_s3(images, s3_bucket_name):
    urls = []
    for img in images:
        key = f"output/{uuid.uuid4()}.png"
        s3.put_object(Bucket=s3_bucket_name, Key=key, Body=img.getvalue())
        urls.append(f"s3://{s3_bucket_name}/{key}")
    return urls

# Utility functions

def get_bytesio_from_bytes(image_bytes):
    return BytesIO(image_bytes)

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

def get_claude_outpainting_prompt_content_request_body(prompt_content):
    system_prompt = """
    You are an expert prompt engineer for the Amazon Titan Image Generator. Your task is to translate intputs to English and create optimal prompts (in English, with fewer than 512 characters) based on user inputs. You will receive various details about the desired image, and your job is to synthesize this information into a cohesive, detailed prompt (in English) that will guide Titan in generating a high-quality image.
    Follow these guidelines when crafting the prompt:

    1. VERY IMPORTANT: If any part of the input is not entirely in English, translate it to English.

    2. Analyze the prompt and identify opportunities for enhancement based on these key principles:
    - Use vivid, specific language to capture key visual details
    - Consider the overall style and tone
    - Structure the prompt logically, using punctuation effectively
    - Add guiding details about objects, colors, lighting, and background
    - Include relevant context that complements the main subject
    - Specify lighting and atmosphere to set the mood
    - For product-related prompts, create a narrative or lifestyle context

    3. Expand and refine the prompt, incorporating the above principles. Aim for a prompt length of 2-4 sentences. VERY IMPORTANT: The prompt has to be 512 characters or less (including spaces and punctuation).
    
    4. If the original prompt lacked specific style guidance, consider adding style keywords like "photorealistic", "cinematic lighting", etc.

    5. Check again that the prompt is in English and ONLY in English. This is extremely important. Make sure this is your top priority.

    6. Check again that the total number of prompt characters is fewer than 512 (including spaces and punctuation). If it's 512 characters or less, shorten the prompt. This is extremely important. Make this your top priority.

    Remember, your goal is to create a prompt (in English) that will result in a detailed, cohesive, and visually striking image that matches the user's intentions.

    VERY IMPORTANT: The output will only contain the updated prompt. Do not add any words.
    VERY IMPORTANT: The output has to be 512 characters or less (including spaces and punctuation).
    VERY IMPORTANT: The output must be in English and only in English

    Before providing the answer, make sure the output is in English and the number of characters is fewer than 512 (including spaces and punctuations).
    DO NOT provide the output unless the output is in English and only in English and the total number of characters do not exceed 512.

    Provide the English prompt:
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

def get_claude_inpainting_prompt_content_request_body(prompt_content):
    system_prompt = """
    You are an expert prompt engineer for the Amazon Titan Image Generator. Your task is to translate inputs to English and create optimal prompts (in English) for inpainting based on user inputs. You will receive various details about the desired image, and your job is to synthesize this information into a cohesive, detailed prompt (in English) that will guide Titan in generating a high-quality image.
    Follow these guidelines when crafting the prompt:

    1. VERY IMPORTANT: If any part of the input is not entirely in English, translate it to English.

    2. Briefly mention the original image and the area to be modified. Analyze the prompt and identify opportunities for enhancement based on these key principles:
    - Describe the new element(s) in detail, using vivid and specific language.
    - Incorporate the desired style and mood.
    - If provided, mention color preferences and specific details to include.
    - Explain how the new element(s) should integrate with the existing image.
    - Structure the prompt logically, using commas to separate elements.
    - If necessary, add style keywords at the end of the prompt.

    3. Keep the prompt length to 2-3 sentences while including all crucial information. VERY IMPORTANT: The prompt has to be 512 characters or less (including spaces and punctuation).
    
    4. If the original prompt lacked specific style guidance, consider adding style keywords like "photorealistic", "cinematic lighting", etc.

    5. Check again that the prompt is in English and ONLY in English. This is extremely important.

    6. Check again that the total number of prompt characters is fewer than 512 (including spaces and punctuation). If it's 512 characters or less (including spaces and punctuation), shorten the prompt. This is extremely important.

    Remember, your goal is to create a prompt (in English) that will result in a detailed, cohesive, and visually striking image that matches the user's intentions.

    VERY IMPORTANT: The output will only contain the updated prompt. Do not add any words.
    VERY IMPORTANT: The output has to be 512 characters or less (including spaces and punctuation).
    VERY IMPORTANT: The output must be in English and only in English

    Before providing the answer, make sure the output is in English and the number of characters is fewer than 512 (including spaces and punctuations).
    DO NOT provide the output unless the output is in English and only in English and the total number of characters do not exceed 512.

    Provide the English prompt:
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

def get_titan_image_masking_request_body(prompt_content, image_bytes, painting_mode, masking_mode, mask_prompt, num_output_images):
    original_image = get_image_from_bytes(image_bytes)
    target_width, target_height = original_image.size
    image_base64 = get_base64_from_bytes(image_bytes)
    mask_base64 = None
    
    body = {
        "taskType": painting_mode,
        "imageGenerationConfig": {
            "numberOfImages": num_output_images,
            "quality": "premium",
            "height": target_height,
            "width": target_width,
            "cfgScale": 8.0,
            "seed": randint(0, 100000),
        },
    }
    
    params = {
        "image": image_base64,
        "text": prompt_content,
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
    return image_data_list

def get_image_from_model(prompt_content, image_bytes, painting_mode, masking_mode, mask_prompt=None, num_output_images=5):
    bedrock = boto3.client(service_name='bedrock-runtime')

    mask_prompt_request_body = get_claude_mask_prompt_request_body(mask_prompt)
    if painting_mode == "OUTPAINTING":
        prompt_content_request_body = get_claude_outpainting_prompt_content_request_body(prompt_content)
    else:
        prompt_content_request_body = get_claude_inpainting_prompt_content_request_body(prompt_content)

    start = time.time()
    print("Current time:", start)
    print("Invoking Claude v3 Sonnet on Amazon Bedrock..")
    mask_prompt_response = bedrock.invoke_model(body=mask_prompt_request_body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")
    prompt_content_response = bedrock.invoke_model(body=prompt_content_request_body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")

    translated_mask_prompt = get_claude_response_text(mask_prompt_response)
    translated_prompt_content = get_claude_response_text(prompt_content_response)

    after_claude_time = time.time() - start
    print("after claude execution:", after_claude_time)

    image_request_body = get_titan_image_masking_request_body(translated_prompt_content, image_bytes, painting_mode, masking_mode, translated_mask_prompt, num_output_images)
    
    print("Invoking Amazon Titan Image Generator on Amazon Bedrock..")
    response = bedrock.invoke_model(body=image_request_body, modelId="amazon.titan-image-generator-v1", contentType="application/json", accept="application/json")

    after_titan_time = time.time() - start
    print("after titan execution:", after_titan_time)
    
    output_image = get_titan_response_image(response)
    
    return [output_image, translated_mask_prompt, translated_prompt_content]

def health_check():
    return {
        'statusCode': 200,
        'body': json.dumps('Healthy'),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
