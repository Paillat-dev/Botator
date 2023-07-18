import logging
import sqlite3
import json
from dotenv import load_dotenv
import os

# Loading environement variables
load_dotenv()

perspective_api_key = os.getenv("PERSPECTIVE_API_KEY")
discord_token = os.getenv("DISCORD_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")
max_uses: int = 400
tenor_api_key = os.getenv("TENOR_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)

# Setting up the google vision api
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./../database/google-vision/botator.json"

# Defining a debug function

def debug(message):
    if os.name == "nt":
        logging.info(message)
    else:
        print(message)


def ctx_to_guid(ctx):
    if ctx.guild is None:
        return ctx.author.id
    else:
        return ctx.guild.id


def mg_to_guid(mg):
    if mg.guild is None:
        return mg.author.id
    else:
        return mg.guild.id


con_data = sqlite3.connect("./database/data.db")
curs_data = con_data.cursor()
con_premium = sqlite3.connect("./database/premium.db")
curs_premium = con_premium.cursor()

curs_data.execute(
    """CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)"""
)
# we delete the moderation table and create a new one, with all theese parameters as floats: TOXICITY: {result[0]}; SEVERE_TOXICITY: {result[1]}; IDENTITY ATTACK: {result[2]}; INSULT: {result[3]}; PROFANITY: {result[4]}; THREAT: {result[5]}; SEXUALLY EXPLICIT: {result[6]}; FLIRTATION: {result[7]}; OBSCENE: {result[8]}; SPAM: {result[9]}
expected_columns = 14

# we delete the moderation table and create a new one
curs_data.execute(
    """CREATE TABLE IF NOT EXISTS moderation (guild_id text, logs_channel_id text, is_enabled boolean, mod_role_id text, toxicity real, severe_toxicity real, identity_attack real, insult real, profanity real, threat real, sexually_explicit real, flirtation real, obscene real, spam real)"""
)

# This code returns the number of columns in the table "moderation" in the database "data.db".
curs_data.execute("PRAGMA table_info(moderation)")
result = curs_data.fetchall()
actual_columns = len(result)

if actual_columns != expected_columns:
    # we add the new columns
    curs_data.execute("ALTER TABLE moderation ADD COLUMN toxicity real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN severe_toxicity real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN identity_attack real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN insult real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN profanity real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN threat real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN sexually_explicit real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN flirtation real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN obscene real")
    curs_data.execute("ALTER TABLE moderation ADD COLUMN spam real")
else:
    print("Table already has the correct number of columns")

# This code creates the model table if it does not exist
curs_data.execute(
    """CREATE TABLE IF NOT EXISTS model (guild_id text, model_name text)"""
)

# This code creates the images table if it does not exist
curs_data.execute(
    """CREATE TABLE IF NOT EXISTS images (guild_id text, usage_count integer, is_enabled boolean)"""
)

# This code creates the data table if it does not exist
curs_premium.execute(
    """CREATE TABLE IF NOT EXISTS data (user_id text, guild_id text, premium boolean)"""
)

# This code creates the channels table if it does not exist
curs_premium.execute(
    """CREATE TABLE IF NOT EXISTS channels (guild_id text, channel0 text, channel1 text, channel2 text, channel3 text, channel4 text)"""
)
