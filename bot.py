import asyncio
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN
from modules import stabledif, gemini, database, load

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!cucumberai", intents=intents)

load.commands(bot)
database.setup_db()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    response = gemini.get_model_response(message)

    if "IMAGE GENERATION:" in response:
        asyncio.create_task(stabledif.SendImage(response, message.channel))
    else:
        asyncio.create_task(gemini.SendText(response, message.channel))

    database.update_channel_history(message, response)
    await bot.process_commands(message)

@bot.event
async def on_ready():
    bot.loop.create_task(database.clear_old_histories())
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")

bot.run(DISCORD_BOT_TOKEN, reconnect=True)