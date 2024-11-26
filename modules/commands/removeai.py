from discord.ext import commands
from modules.database import db_cursor, db_connection
import discord

def setup(bot):
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.AppCommandError
    async def error(interaction : discord.Interaction):
        await interaction.response.send_message("You don't have permissions to use this command")
    @bot.tree.command(name="ai-remove", description="Remove AI setup for a specific channel")
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