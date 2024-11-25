# cucumberAI

**cucumberAI** is a simple Discord chatbot and image generation tool. It's powered by the Gemini API and Hugging Face's Stable Diffusion 3.5 Large API.

For support or access to a hosted version of the bot (if you don't want to deploy it yourself), join the [official support Discord server](https://discord.gg/awJMWYgV5c).

---

## Features
- **Chatbot:** Engage in interactive conversations based on custom personalities.
- **Image Generation:** Create images using text prompts and Stable Diffusion integration.
- **Customizable:** Easily set up custom personalities and adjust bot behavior.
- **Automatic Cleanup:** Message history clears after 10 minutes of inactivity.

---

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/FrenZy931/cucumberAI
   cd cucumberAI

2. **Set up API keys:**
    Open config.py.
    Add your:
        1. Discord bot token.
        2. Gemini API key.
        3. Hugging Face API key.

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Run the bot:**
    ```bash
    python3 bot.py

---

## Commands Usage
**Setup AI in a channel:**
    /ai-setup <channel> <personality>
    Assigns the bot to a channel and applies a custom personality.


**Clear history:**
    /clear-history <channel>
    Deletes chat history for the specified channel.


**Remove AI:**
    /ai-remove <channel>
    Disconnects the bot from the specified channel.

---

## How It Works
**Initialization:**
    The bot initializes by checking for the existence of ai.db:
    If absent, it creates the database and sets up tables for:
        History: Stores conversation logs.
        Channels: Tracks channel configurations.
        Personalities: Manages user-defined behavior.

**Commands**
    All commands (e.g., /ai-setup, /clear-history) are registered and ready to interact with users.

**Message Handling**
    The bot listens to messages in configured channels via on_message.
    If the message requires:
        Text generation, it sends the prompt and context (history, instructions, personality) to Gemini.
        Image generation, the prompt is forwarded to Stable Diffusion.

**Custom Instruction Handling**
    instructions.txt: Provides the AI with structured guidelines for processing prompts.
    personality.txt: Allows users to create custom personalities and add unique behavior to the bot.


**Image and Text Integration**
    Responses containing image requests are detected via delimiters (e.g., |IMAGE GENERATION ...|).
I   mages and text are merged seamlessly, ensuring the response appears cohesive to users.



---

## License

This project is released under the MIT License.


---

Thanks for using cucumberAI! 