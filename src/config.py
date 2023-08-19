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

con_data.execute('CREATE TABLE IF NOT EXISTS setup_data (guild_id text, guild_settings text)')

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

with open(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "./prompts/gpt-3.5-turbo.txt")
    ),
    "r",
    encoding="utf-8",
) as file:
    gpt_3_5_turbo_prompt = file.read()
