from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from config import GEMINI_API_KEY
from modules import load, database
import google.generativeai as genai

personalities = load.personalities()
instructions = load.instructions()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

generation_config = GenerationConfig(  
    temperature=2,
    max_output_tokens=2000
)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def GenerateText(prompt):
    try:
        response = model.generate_content(prompt, safety_settings=safety_settings, generation_config=generation_config)
        if not response.candidates:
            return "Response blocked due to prohibited content."
        return response.text
    except Exception as e:
        return "Error generating response."

async def SendText(response, channel):
    text_message = await channel.send("Generating response, please wait...")        
    await text_message.delete()
    await channel.send(response)

def get_model_response(message):
    input_text = message.content
    personality = database.get_personality(message)[0]
    personality_content = personalities.get(personality, "")
    chat_history = database.get_channel_history(message.guild.id, message.channel.id)

    prompt = (
        f"|INSTRUCTIONS: {instructions}END OF INSTRUCTIONS|"
        f"|THIS IS CHAT HISTORY:{chat_history} THIS IS END OF CHAT HISTORY|"
        f"|PERSONALITY START: {personality_content}PERSONALITY END|"
        f"|PROMPT: {input_text} END OF PROMPT|"
    )
    output = GenerateText(prompt)

    if "|GENERATE IMAGE" in output and "GENERATE IMAGE|" in output:
        start_index = output.find("|GENERATE IMAGE") + len("|GENERATE IMAGE")
        end_index = output.find("GENERATE IMAGE|")
        image_prompt = output[start_index:end_index].strip()

        return f"IMAGE GENERATION:{output[:start_index]}{image_prompt}{output[end_index + len('GENERATE IMAGE|'):]}"

    return output