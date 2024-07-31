import boto3
import os
import json
import base64
from PIL import Image
from io import BytesIO
from random import randint
import requests
import uuid

API_URL = os.environ.get("API_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")


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


def query_generate_image_lambda(prompt_content, image_bytes, painting_mode, masking_mode, mask_bytes=None, mask_prompt=None, num_output_images=5):
    s3 = boto3.client('s3')

    # Upload input image to S3
    input_image_key = f"input/{uuid.uuid4()}.png"
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=input_image_key, Body=image_bytes)
    input_image_url = f"s3://{S3_BUCKET_NAME}/{input_image_key}"

    payload = {
        "prompt_content": prompt_content,
        "image_url": input_image_url,
        "s3_bucket_name": S3_BUCKET_NAME,
        "painting_mode": painting_mode,
        "masking_mode": masking_mode,
        "mask_prompt": mask_prompt,
        "num_output_images": num_output_images
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200: 
        result = response.json()
        image_urls = result['image_urls']
        translated_mask_prompt = result['translated_mask_prompt']
        translated_prompt_content = result['translated_prompt_content']

        # Retrieve the images from S3
        output_images = []
        for s3_url in image_urls:
            object_key = '/'.join(s3_url.split('/')[3:])
            s3_response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=object_key)
            image_data = s3_response['Body'].read()
            output_images.append(BytesIO(image_data))
    
        return [output_images, translated_mask_prompt, translated_prompt_content]
    else:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

    