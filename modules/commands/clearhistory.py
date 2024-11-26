from discord.ext import commands
from modules.database import db_cursor, db_connection
import discord

def setup(bot):
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.AppCommandError
    async def error(interaction : discord.Interaction):
        await interaction.response.send_message("You don't have permissions to use this command")
    @bot.tree.command(name="clear-ai-history", description="Removes history for specific channel")
    async def clear_ai_history(interaction: discord.Interaction, channel: discord.TextChannel):
        with db_connection:
                db_cursor.execute("UPDATE channels SET history = '' WHERE server_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
                db_connection.commit()
                await interaction.response.send_message(f"History for {channel.mention} has been removed.")