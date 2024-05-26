import os
import io
import cv2
import numpy as np
from google.cloud import vision
from PIL import Image

# Function to analyze the image using Google Vision API
def analyze_image(image_path):
    try:
        client = vision.ImageAnnotatorClient()

        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"API Error: {response.error.message}")

        return response

    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return None

# Function to extract text from the Google Vision API response
def extract_text(response):
    try:
        texts = response.text_annotations
        extracted_text = ""
        if texts:
            extracted_text = texts[0].description
        return extracted_text

    except Exception as e:
        print(f"Error in extract_text: {e}")
        return ""

# Function to segment visual elements using OpenCV
def segment_visual_elements(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        visual_elements = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            visual_elements.append(image[y:y+h, x:x+w])

        return visual_elements

    except Exception as e:
        print(f"Error in segment_visual_elements: {e}")
        return []

# Function to save visual elements as images and create an HTML string
def create_html(text, visual_elements):
    try:
        html_content = "<html><head><style>img {max-width: 100%; height: auto;} body {font-family: Arial, sans-serif;}</style></head><body>"

        # Add text as paragraphs
        paragraphs = text.split('\n')
        for para in paragraphs:
            if para.strip():
                html_content += f"<p>{para}</p>"

        # Save visual elements as images and embed in HTML
        for i, element in enumerate(visual_elements):
            img_path = f"visual_element_{i}.png"
            cv2.imwrite(img_path, element)
            html_content += f'<img src="{img_path}" alt="Visual Element {i}"><br>'

        html_content += "</body></html>"
        return html_content

    except Exception as e:
        print(f"Error in create_html: {e}")
        return ""

# Function to save HTML content to a file
def save_html(html_content, file_name='output.html'):
    try:
        with open(file_name, 'w') as file:
            file.write(html_content)
        print(f"HTML content successfully saved to {file_name}")

    except Exception as e:
        print(f"Error in save_html: {e}")

# Main function to orchestrate the entire process
def main(image_path):
    try:
        # Step 1: Analyze the image
        response = analyze_image(image_path)
        if response is None:
            print("Failed to analyze image.")
            return

        # Step 2: Extract text from the analyzed image
        text = extract_text(response)
        if not text:
            print("No text found in image.")
            return

        # Step 3: Segment visual elements
        visual_elements = segment_visual_elements(image_path)
        if not visual_elements:
            print("No visual elements found in image.")
            return

        # Step 4: Create HTML content
        html_content = create_html(text, visual_elements)
        if not html_content:
            print("Failed to create HTML content.")
            return

        # Step 5: Save HTML content to a file
        save_html(html_content)

    except Exception as e:
        print(f"Error in main: {e}")

# Entry point of the script
if __name__ == "__main__":
    image_path = 'img1.jpg'
    if not os.path.exists(image_path):
        print(f"Image file {image_path} does not exist.")
    else:
        main(image_path)
