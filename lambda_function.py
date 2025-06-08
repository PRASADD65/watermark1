import json
import boto3
from PIL import Image, ImageDraw, ImageFont
import io
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        image = Image.open(io.BytesIO(image_data))
        
        watermark_text = "CloudFolks HUB"
        draw = ImageDraw.Draw(image)
        
        try:
            font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'arial.ttf')
            font = ImageFont.truetype(font_path, 40)
            print(f"Loaded custom font from {font_path}")
        except IOError:
            font = ImageFont.load_default()
            print("Loaded default font")

        # Calculate text position for center alignment
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        width, height = image.size
        text_position = ((width - text_width) / 2, (height - text_height) / 2)

        # Debugging output for text position and image size
        print(f"Image size: {width}x{height}")
        print(f"Text size: {text_width}x{text_height}")
        print(f"Text position: {text_position}")
        
        draw.text(text_position, watermark_text, font=font, fill='red')
        print("Watermark applied")

        image_format = image.format if image.format else 'JPEG'
        buffer = io.BytesIO()
        image.save(buffer, format=image_format)
        buffer.seek(0)

        base_filename = os.path.basename(key)
        new_key = f'watermarked/{base_filename}'

        print(f"Uploading watermarked image to {new_key} in bucket {bucket}")
        s3.put_object(Bucket=bucket, Key=new_key, Body=buffer, ContentType=f'image/{image_format.lower()}')
        print("Upload successful")
        
        return {'statusCode': 200, 'body': json.dumps('Watermark added successfully!')}
    
    except Exception as e:
        print(f"Error processing {key} from bucket {bucket}: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps('Error processing the image')}

