import sqlite3
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()
import time
#the database is: c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)''')
#set the uses_count_today to 0 for all guilds every 24 hours
while True:
    c.execute("UPDATE data SET uses_count_today = 0")
    conn.commit()
    time.sleep(86400)