import logging
import sqlite3
from dotenv import load_dotenv
import os
load_dotenv()
perspective_api_key = os.getenv("PERSPECTIVE_API_KEY")
max_uses: int = 400
logging.basicConfig(level=logging.INFO)

def debug(message):
    logging.info(message)
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()
connp = sqlite3.connect('../database/premium.db')
cp = connp.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)''')
c.execute('''CREATE TABLE IF NOT EXISTS moderation (guild_id text, logs_channel_id text, is_enabled boolean, mod_role_id text)''')
cp.execute('''CREATE TABLE IF NOT EXISTS data (user_id text, guild_id text, premium boolean)''')
cp.execute('''CREATE TABLE IF NOT EXISTS channels (guild_id text, channel0 text, channel1 text, channel2 text, channel3 text, channel4 text)''')