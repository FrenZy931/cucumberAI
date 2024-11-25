from huggingface_hub import InferenceClient
from config import HUGGING_FACE_API_KEY
from PIL import Image
from io import BytesIO

def GenerateImage(image_input):
    try:
        client = InferenceClient(model="stabilityai/stable-diffusion-3.5-large", token=HUGGING_FACE_API_KEY)
        image = client.text_to_image(image_input)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None