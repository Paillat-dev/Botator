import logging
import sqlite3
from dotenv import load_dotenv
import os
import openai
load_dotenv()
perspective_api_key = os.getenv("PERSPECTIVE_API_KEY")
discord_token = os.getenv("DISCORD_TOKEN")
max_uses: int = 400
logging.basicConfig(level=logging.INFO)

def debug(message):
    logging.info(message)
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()
connp = sqlite3.connect('../database/premium.db')
cp = connp.cursor()

async def moderate(api_key, text):
    openai.api_key = api_key
    response = await openai.Moderation.acreate(
        input=text,
        )
    return response["results"][0]["flagged"]

c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)''')
#we delete the moderation table and create a new one, with all theese parameters as floats: TOXICITY: {result[0]}; SEVERE_TOXICITY: {result[1]}; IDENTITY ATTACK: {result[2]}; INSULT: {result[3]}; PROFANITY: {result[4]}; THREAT: {result[5]}; SEXUALLY EXPLICIT: {result[6]}; FLIRTATION: {result[7]}; OBSCENE: {result[8]}; SPAM: {result[9]}
expected_columns = 14

#we delete the moderation table and create a new one
c.execute('''CREATE TABLE IF NOT EXISTS moderation (guild_id text, logs_channel_id text, is_enabled boolean, mod_role_id text, toxicity real, severe_toxicity real, identity_attack real, insult real, profanity real, threat real, sexually_explicit real, flirtation real, obscene real, spam real)''')
c.execute("PRAGMA table_info(moderation)")
result = c.fetchall()
actual_columns = len(result)
if actual_columns != expected_columns:
    #we add the new columns
    c.execute("ALTER TABLE moderation ADD COLUMN toxicity real")
    c.execute("ALTER TABLE moderation ADD COLUMN severe_toxicity real")
    c.execute("ALTER TABLE moderation ADD COLUMN identity_attack real")
    c.execute("ALTER TABLE moderation ADD COLUMN insult real")
    c.execute("ALTER TABLE moderation ADD COLUMN profanity real")
    c.execute("ALTER TABLE moderation ADD COLUMN threat real")
    c.execute("ALTER TABLE moderation ADD COLUMN sexually_explicit real")
    c.execute("ALTER TABLE moderation ADD COLUMN flirtation real")
    c.execute("ALTER TABLE moderation ADD COLUMN obscene real")
    c.execute("ALTER TABLE moderation ADD COLUMN spam real")
else:
    print("Table already has the correct number of columns")
    pass
c.execute('''CREATE TABLE IF NOT EXISTS model (guild_id text, model_name text)''')
cp.execute('''CREATE TABLE IF NOT EXISTS data (user_id text, guild_id text, premium boolean)''')
cp.execute('''CREATE TABLE IF NOT EXISTS channels (guild_id text, channel0 text, channel1 text, channel2 text, channel3 text, channel4 text)''')