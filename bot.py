import asyncio
from io import BytesIO
import time
import typing
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN
import os
import sqlite3
from modules.image import GenerateImage
from modules.chat import GenerateText

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

db_connection = sqlite3.connect("ai.db", check_same_thread=False, timeout=10)
db_cursor = db_connection.cursor()

def setup_db():
    with db_connection:
        db_cursor.execute(
            '''CREATE TABLE IF NOT EXISTS channels (
                server_id TEXT, 
                channel_id TEXT, 
                history TEXT, 
                personality TEXT, 
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
        )

setup_db()

def save_server_config(server_id, channel_id, personality):
    with db_connection:
        db_cursor.execute(
            "INSERT OR REPLACE INTO channels (server_id, channel_id, personality) VALUES (?, ?, ?)",
            (server_id, channel_id, personality),
        )

def load_instructions(file_path="instructions.txt"):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return "No instructions found."

def load_personalities(personalities_folder="personalities"):
    personalities = {}
    if os.path.exists(personalities_folder):
        for filename in os.listdir(personalities_folder):
            if filename.endswith(".txt"):
                with open(os.path.join(personalities_folder, filename), "r") as file:
                    personality_name = filename.replace(".txt", "")
                    personalities[personality_name] = file.read()
    return personalities

personalities = load_personalities()

@discord.app_commands.checks.has_permissions(administrator=True)
@discord.app_commands.AppCommandError
async def error(interaction : discord.Interaction):
    await interaction.response.send_message("You don't have permissions to use this command")
@bot.tree.command(name="clear_ai_history", description="Removes history for specific channel")
async def clear_ai_history(interaction: discord.Interaction, channel: discord.TextChannel):
    with db_connection:
            db_cursor.execute("UPDATE channels SET history = '' WHERE server_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
            db_connection.commit()
            await interaction.response.send_message(f"History for {channel.mention} has been removed.")

@discord.app_commands.checks.has_permissions(administrator=True)
@discord.app_commands.AppCommandError
async def error(interaction : discord.Interaction):
    await interaction.response.send_message("You don't have permissions to use this command")
@bot.tree.command(name="ai_remove", description="Remove AI setup for a specific channel")
async def ai_remove(interaction: discord.Interaction, channel: discord.TextChannel):
    with db_connection:
        db_cursor.execute("SELECT * FROM channels WHERE server_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
        result = db_cursor.fetchone()

        if result:
            db_cursor.execute("DELETE FROM channels WHERE server_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
            db_connection.commit()
            await interaction.response.send_message(f"AI setup for {channel.mention} has been removed.")
        else:
            await interaction.response.send_message(f"No AI setup found for {channel.mention}.")

@discord.app_commands.checks.has_permissions(administrator=True)
@discord.app_commands.AppCommandError
async def error(interaction : discord.Interaction):
    await interaction.response.send_message("You don't have permissions to use this command")
@bot.tree.command(name="ai_setup", description="Setup or update AI with personality for a specific channel")
async def ai_setup(interaction: discord.Interaction, channel: discord.TextChannel, personality: typing.Literal['Default', 'discordcucumber', 'girlfriend']):
    with db_connection:
        db_cursor.execute("SELECT * FROM channels WHERE server_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
        result = db_cursor.fetchone()
        if result:
            db_cursor.execute(
                "UPDATE channels SET personality = ?, history = '', last_updated = CURRENT_TIMESTAMP WHERE server_id = ? AND channel_id = ?",
                (personality, interaction.guild.id, channel.id),
            )
            await interaction.response.send_message(
                f"AI setup for {channel.mention} updated. Personality changed to {personality}."
            )
        else:
            db_cursor.execute(
                "INSERT INTO channels (server_id, channel_id, personality, history) VALUES (?, ?, ?, '')",
                (interaction.guild.id, channel.id, personality),
            )
            await interaction.response.send_message(
                f"AI setup for {channel.mention} created with personality {personality}."
            )
        db_connection.commit()

def get_model_response(input_text, personality_content, chat_history):
    instructions = load_instructions()
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

        return f"Generating image, please wait...\n{output[:start_index]}{image_prompt}{output[end_index + len('GENERATE IMAGE|'):]}"

    return output

def get_channel_history(server_id, channel_id):
    try:
        db_cursor.execute("SELECT history FROM channels WHERE server_id=? AND channel_id=?", (server_id, channel_id))
        result = db_cursor.fetchone()
        return result[0] if result and result[0] else ""
    except sqlite3.OperationalError as e:
        return ""

def save_channel_history(server_id, channel_id, new_message):
    retry_count = 3
    while retry_count > 0:
        try:
            with db_connection:
                db_cursor.execute(
                    "UPDATE channels SET history = ?, last_updated = CURRENT_TIMESTAMP WHERE server_id = ? AND channel_id = ?",
                    (new_message, server_id, channel_id),
                )
                if db_cursor.rowcount == 0:
                    pass
            return
        except sqlite3.OperationalError:
            retry_count -= 1
            time.sleep(1)

async def clear_old_histories():
    while True:
        await asyncio.sleep(60)
        with db_connection:
            db_cursor.execute(
                "UPDATE channels SET history = '' WHERE last_updated < datetime('now', '-10 minutes')"
            )
            db_connection.commit()

async def SendText(response, channel):
    text_message = await channel.send("Generating response, please wait...")        
    await text_message.delete()
    await channel.send(response)

async def SendImage(response, channel):
    try:
        image_generation_text = await channel.send("Generating image, please wait...")
        image_prompt = response.split("Generating image, please wait...\n")[1].strip()
        image_data = await asyncio.to_thread(GenerateImage, image_prompt)
        response = response.replace(f"Generating image, please wait...", "")
        response = response.split("|GENERATE IMAGE")[0]
        reply = response
        response = ""
        await image_generation_text.delete()
        await channel.send(reply, file=discord.File(image_data, filename="generated_image.png"))
    except Exception as e:
        await image_generation_text.delete()
        await channel.send(f"An error occurred while generating the image: sd3.5 delay exceeded, exiting program.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    db_cursor.execute(
        "SELECT personality FROM channels WHERE server_id=? AND channel_id=?", 
        (message.guild.id, message.channel.id)
    )
    result = db_cursor.fetchone()

    if result:
        personality = result[0]
        personality_content = personalities.get(personality, "")
        chat_history = get_channel_history(message.guild.id, message.channel.id)
        response = get_model_response(message.content, personality_content, chat_history)

        if "|GENERATE IMAGE" in response:
            asyncio.create_task(SendImage(response, message.channel))
        else:
            asyncio.create_task(SendText(response, message.channel))

        user_message = f"{message.author.name}: {message.content}"
        ai_response = f"AI: {response}"
        save_channel_history(message.guild.id, message.channel.id, f"{chat_history}{user_message}\n{ai_response}")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(clear_old_histories())
    print(f"Logged in as {bot.user.name}")

bot.run(DISCORD_BOT_TOKEN, reconnect=True)