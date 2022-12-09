import logging
import sqlite3
max_uses: int = 500
logging.basicConfig(level=logging.INFO)

def debug(message):
    logging.info(message)

#create a database called "database.db" if the database does not exist, else connect to it
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()
connp = sqlite3.connect('../database/premium.db')
cp = conn.cursor()

# Create table called "data" if it does not exist with the following columns: guild_id, channel_id, api_key, is_active, max_tokens, temperature, frequency_penalty, presence_penalty, uses_count_today, prompt_size
c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)''')
cp.execute('''CREATE TABLE IF NOT EXISTS data (user_id text, guild_id text, premium boolean)''')