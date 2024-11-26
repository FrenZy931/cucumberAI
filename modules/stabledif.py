import discord
import asyncio
from huggingface_hub import InferenceClient
from config import HUGGING_FACE_API_KEY
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
    
async def SendImage(response, channel):
    image_generation_text = await channel.send("Generating response, please wait...")
    image_prompt = response.split("IMAGE GENERATION:")[1].strip()
    image_data = await asyncio.to_thread(GenerateImage, image_prompt)
    if image_data:
        response = response.replace(f"IMAGE GENERATION:", "")
        response = response.split("|GENERATE IMAGE")[0]
        reply = response
        response = ""
        await image_generation_text.delete()
        await channel.send(reply, file=discord.File(image_data, filename="generated_image.png"))
    else:
        await image_generation_text.delete()
        await channel.send("Failed to generate image.")