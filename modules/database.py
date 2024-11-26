import sqlite3
import time
import os
import asyncio

db_connection = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai.db"), check_same_thread=False, timeout=10)
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

def save_server_config(server_id, channel_id, personality):
    with db_connection:
        db_cursor.execute(
            "INSERT OR REPLACE INTO channels (server_id, channel_id, personality) VALUES (?, ?, ?)",
            (server_id, channel_id, personality),
        )

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

def update_channel_history(message, response):
    user_message = f"{message.author.name}: {message.content}"
    ai_response = f"AI: {response}"
    save_channel_history(message.guild.id, message.channel.id, f"{get_channel_history(message.guild.id, message.channel.id)}{user_message}\n{ai_response}")

def get_personality(message):
    db_cursor.execute(
        "SELECT personality FROM channels WHERE server_id=? AND channel_id=?", 
        (message.guild.id, message.channel.id)
    )
    return db_cursor.fetchone()