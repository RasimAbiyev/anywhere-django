# Working with image. (Watermark, Crop, Thumbnail)
import os
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image as PILImage, ImageDraw, ImageFont

def add_watermark(image_path, watermark_path, output_path):

    try:
        with PILImage.open(image_path) as original:
            original = original.convert('RGBA')
            with PILImage.open(watermark_path) as watermark:
                watermark = watermark.convert('RGBA')
                
                watermarked = PILImage.new('RGBA', original.size)
                watermarked.paste(original, (0, 0))
                
                watermark_position = (
                    (original.width - watermark.width) // 2,
                    (original.height - watermark.height) // 2
                )
                
                watermarked.paste(watermark, watermark_position, watermark)
                
                watermarked_rgb = watermarked.convert('RGB')
                watermarked_rgb.save(output_path, 'JPEG')
                
                print("Watermark added successfully!")
    except Exception as e:
        print(f"An error occurred while adding watermark: {e}")

def crop_image(image_path, crop_box, output_path):

    try:
        with PILImage.open(image_path) as img:
            img = img.convert('RGBA')
            cropped_img = img.crop(crop_box)
            
            if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                cropped_img_rgb = cropped_img.convert('RGB')
                cropped_img_rgb.save(output_path, 'JPEG')
            else:
                cropped_img.save(output_path, 'PNG')
            
            print("Image cropped successfully!")
    except Exception as e:
        print(f"An error occurred while cropping image: {e}")

def create_thumbnail(image_path, thumbnail_size, output_path):
    
    try:
        with PILImage.open(image_path) as img:
            img = img.convert('RGBA')
            img.thumbnail(thumbnail_size)
            
            if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                img_rgb = img.convert('RGB')
                img_rgb.save(output_path, 'JPEG')
            else:
                img.save(output_path, 'PNG')
            
            print("Thumbnail created successfully!")
    except Exception as e:
        print(f"An error occurred while creating thumbnail: {e}")