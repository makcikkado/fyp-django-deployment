# open and encode image
from PIL import Image
import base64
import requests
import os
import json
from io import BytesIO 
from dotenv import load_dotenv

load_dotenv()


# API deets
# API_URL = "https://syxb3tv0k8qzns7n.eastus.azure.endpoints.huggingface.cloud"
# API_URL = "https://api-inference.huggingface.co/models/google/paligemma-3b-mix-224"
# API_URL = "https://u82hvbndio7vxg1a.us-east-1.aws.endpoints.huggingface.cloud" #URL FOR GPU ENDPOINT
# API_URL = "https://orzdi93u110eng59.us-east-1.aws.endpoints.huggingface.cloud"
# API_URL = "https://n4tex9fbyg3sfuf6.eastus.azure.endpoints.huggingface.cloud"
API_URL = "https://lk8smhzww0iyrf1i.eastus.azure.endpoints.huggingface.cloud"
# API_KEY = "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"
API_KEY = os.getenv("HF_API_KEY")

headers = {
    "Accept" : "application/json",
	"Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
    }

# def encode_image(image_path, resize_to=(224,224)):
#     """Convert an image file to a Base64 string."""
#     if not os.path.exists(image_path):
#         return None  # Return None if no image is provided
    
#     with Image.open(image_path) as img:
#         img = img.convert("RGB")
#         img = img.resize(resize_to)
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG")
#         return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
def encode_image(image_path):
    """Convert an image file to a Base64 string."""
    if not os.path.exists(image_path):
        print(f"Image path does not exist: {image_path}")
        return None  # Return None if no image is provided

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def query_paligemma(image_path=None, user_prompt=""):
    """Send image & text input to PaliGemma API and return the response."""
    encoded_image = encode_image(image_path) if image_path else None

    if not encoded_image and not user_prompt:
        return "No image or prompt provided."
    
    # encoded = encode_image("uploads/uploaded_image.jpg")
    # print("Encoded image sample:", encoded[:100])  # Just print the first 100 characters

    # token = JSON.stringify({ image: encoded_image})

    # print("encode imaged:", encoded_image)

    # payload = {
    #     "image": [encoded_image] if encoded_image else [],
    #     "prompt": user_prompt,
    #     "parameters": {
    #         "max_new_tokens": 150
    #     }
    # }

    # Construct the input string for the API
    # input_str = f"![](data:image/jpeg;base64,{encoded_image}) {user_prompt}"

    # payload = {
    #     "inputs": input_str,
    #     "parameters": {
    #         "max_new_tokens": 150
    #     }
    # }

    image_uri = f"data:image/jpeg;base64,{encoded_image}"

    payload = {
        "inputs": {
            "images": image_uri,
            "text": user_prompt
        },
        "parameters": {
            "max_new_tokens": 150
        }
    }

    # prompt_with_image = json.dumps({
    #     "image": encoded_image,
    #     "prompt": user_prompt
    # })

    # inputs_payload = f"![]({encoded_image}){user_prompt}"

    # payload = {
    #     "inputs": "![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Male_cheetah_facing_left_in_South_Africa.jpg/1200px-Male_cheetah_facing_left_in_South_Africa.jpg)caption en",
    #     "parameters": {
    #         "max_new_tokens": 150
    #     }
    # }

    # payload = {
    #     "inputs": {
    #         "image": encoded_image if encoded_image else [],
    #         "prompt": user_prompt
    #     },
    #     "parameters": {
    #         "max_new_tokens": 150
    #     }
    # }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        # return response.json()
    
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get("generated_text", "No output found")
                input_text = result[0].get("input_text", "")
                return generated.replace(input_text, "").strip() if input_text else generated.strip()

                # return result[0].get("generated_text", "No output found").replace(result[0]["input_text"], "").strip()
            else:
                return "No valid output from API"
        else:
            return f"Error {response.status_code}: {response.text}"

    except requests.exceptions.RequestException as e:
        # return f"API request failed: {e}"
        print(response.text)

# Test the function
if __name__ == "__main__":
    print(query_paligemma(image_path="uploads/uploaded_image.jpg", user_prompt="Describe"))

