from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

generation_config = GenerationConfig(  
    temperature=2,
    max_tokens=2000
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