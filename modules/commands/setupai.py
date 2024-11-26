from discord.ext import commands
from modules.database import db_cursor, db_connection
import discord
import typing

def setup(bot):
    @discord.app_commands.checks.has_permissions(administrator=True)
    @discord.app_commands.AppCommandError
    async def error(interaction : discord.Interaction):
        await interaction.response.send_message("You don't have permissions to use this command")
    @bot.tree.command(name="ai-setup", description="Setup or update AI with personality for a specific channel")
    async def ai_setup(interaction: discord.Interaction, channel: discord.TextChannel, personality: typing.Literal['Default', 'GenZ', 'NSFW']):
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