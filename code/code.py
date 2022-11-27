import openai # pip install openai
import discord # pip install pycord
from discord import File, Intents # pip install pycord
import logging # pip install logging
import sqlite3 # pip install sqlite3
import asyncio # pip install asyncio
import os # pip install os

#set the debug mode to the maximum
logging.basicConfig(level=logging.INFO)

def debug(message):
    logging.info(message)

#create a database called "database.db" if the database does not exist, else connect to it
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()

# Create table called "data" if it does not exist with the following columns: guild_id, channel_id, api_key, is_active, max_tokens, temperature, frequency_penalty, presence_penalty, uses_count_today, prompt_size
c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer)''')
Intents=discord.Intents.all() # enable all intents
Intents.members = True
bot = discord.Bot(intents=Intents.all())
#create a command called "setup" that takes 2 arguments: the channel id and the api key
@bot.command()
@discord.commands.option(name="channel_id", description="The channel id", required=True)
@discord.commands.option(name="api_key", description="The api key", required=True)
async def setup(ctx, channel: discord.TextChannel, api_key):
    #check if the api key is valid
    openai.api_key = api_key
    try:
        openai.Completion.create(engine="davinci", prompt="Hello world", max_tokens=1)
    except:
        await ctx.respond("Invalid api key", ephemeral=True)
        return
    #check if the channel is valid
    if channel is None:
        await ctx.respond("Invalid channel id", ephemeral=True)
        return
    #check if the guild is already in the database bi checking if there is a key for the guild
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone()[2] is not None:
        await ctx.respond("This guild is already setup", ephemeral=True)
        return
    #add the guild to the database 
    c.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, channel.id, api_key, False, 150, 1, 0, 0.6, 0, 5))
    conn.commit()
    await ctx.respond("Setup complete", ephemeral=True)
#create a command called "enable" taht only admins can use
@bot.command()
##@discord.commands.permissions(administrator=True)
async def enable(ctx):
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #enable the guild
    c.execute("UPDATE data SET is_active = ? WHERE guild_id = ?", (True, ctx.guild.id))
    conn.commit()
    await ctx.respond("Enabled", ephemeral=True)
#create a command called "disable" that only admins can use
@bot.command()
##@discord.commands.permissions(administrator=True)
async def disable(ctx):
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #disable the guild
    c.execute("UPDATE data SET is_active = ? WHERE guild_id = ?", (False, ctx.guild.id))
    conn.commit()
    await ctx.respond("Disabled", ephemeral=True)
#create a command called "advanced" that only admins can use, wich sets the advanced settings up: max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size
@bot.command()
##@discord.commands.permissions(administrator=True)
#set the first argument: max_tokens, with a default value of 150
@discord.commands.option(name="max_tokens", description="The max tokens", required=False)
#set the second argument: temperature, with a default value of 1
@discord.commands.option(name="temperature", description="The temperature", required=False)
#set the third argument: frequency_penalty, with a default value of 0.5
@discord.commands.option(name="frequency_penalty", description="The frequency penalty", required=False)
#set the fourth argument: presence_penalty, with a default value of 0.5
@discord.commands.option(name="presence_penalty", description="The presence penalty", required=False)
#set the fifth argument: prompt_size, with a default value of 5
@discord.commands.option(name="prompt_size", description="The number of messages to use as a prompt", required=False)
async def advanced(ctx, max_tokens=256, temperature=1, frequency_penalty=0, presence_penalty=0.6, prompt_size=5):
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup, please run /setup", ephemeral=True)
        return
    #update the advanced settings
    c.execute("UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size, ctx.guild.id))
    conn.commit()
    await ctx.respond("The advanced settings have been updated", ephemeral=True)
#create a command called "delete" that only admins can use wich deletes the guild id, the api key, the channel id and the advanced settings from the database
@bot.command()
##@discord.commands.permissions(administrator=True)
async def delete(ctx):
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #delete the guild from the database, except the guild id and the uses_count_today
    c.execute("UPDATE data SET api_key = ?, channel_id = ?, is_active = ?, max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (None, None, False, 50, 0.9, 0.0, 0.0, 0, ctx.guild.id))
    conn.commit()
    await ctx.respond("Deleted", ephemeral=True)
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="Here is the help page", color=0x00ff00)
    embed.add_field(name="/setup", value="Setup the bot", inline=False)
    embed.add_field(name="/enable", value="Enable the bot", inline=False)
    embed.add_field(name="/disable", value="Disable the bot", inline=False)
    embed.add_field(name="/advanced", value="Set the advanced settings", inline=False)
    embed.add_field(name="/delete", value="Delete all your data from our server", inline=False)
    embed.add_field(name="/help", value="Show this message", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)
#when a message is sent into a channel check if the guild is in the database and if the bot is enabled
@bot.command()
async def info(ctx):
    #this command sends all the data about the guild, including the api key, the channel id, the advanced settings and the uses_count_today
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #get all the data from the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    data = c.fetchone()
    #send the data
    embed = discord.Embed(title="Info", description="Here is the info page", color=0x00ff00)
    embed.add_field(name="guild_id", value=data[0], inline=False)
    embed.add_field(name="API Key", value=data[1], inline=False)
    embed.add_field(name="Channel ID", value=data[2], inline=False)
    embed.add_field(name="Is Active", value=data[3], inline=False)
    embed.add_field(name="Max Tokens", value=data[4], inline=False)
    embed.add_field(name="Temperature", value=data[5], inline=False)
    embed.add_field(name="Frequency Penalty", value=data[6], inline=False)
    embed.add_field(name="Presence Penalty", value=data[7], inline=False)
    embed.add_field(name="Prompt Size", value=data[8], inline=False)
    embed.add_field(name="Uses Count Today", value=data[9], inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

@bot.event
async def on_message(message):
    #check if the message is from a bot
    if message.author.bot:
        return
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    if c.fetchone() is None:
        return
    #check if the bot is enabled
    c.execute("SELECT is_active FROM data WHERE guild_id = ?", (message.guild.id,))
    if c.fetchone()[0] == False:
        return
    #check if the message has been sent in the channel set in the database
    c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (message.guild.id,))
    if str(message.channel.id) != str(c.fetchone()[0]):
        debug("The message has been sent in the wrong channel")
        return
    #check if the bot hasn't been used more than 200 times in the last 24 hours (uses_count_today)
    c.execute("SELECT uses_count_today FROM data WHERE guild_id = ?", (message.guild.id,))
    if c.fetchone()[0] >= 200:
        debug("The bot has been used more than 200 times in the last 24 hours in this guild")
        await message.channel.send("The bot has been used more than 200 times in the last 24 hours in this guild. Please try again in 24h.")
        return
    #add 1 to the uses_count_today
    c.execute("UPDATE data SET uses_count_today = uses_count_today + 1 WHERE guild_id = ?", (message.guild.id,))
    #get the api key from the database
    c.execute("SELECT api_key FROM data WHERE guild_id = ?", (message.guild.id,))
    api_key = c.fetchone()[0]
    #get the advanced settings from the database
    c.execute("SELECT max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size FROM data WHERE guild_id = ?", (message.guild.id,))
    max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size = c.fetchone()
    messages = await message.channel.history(limit=prompt_size).flatten()
    messages.reverse()
    prompt = ""
    for msg in messages:
        if msg.author.bot:
            prompt += f"AI: {msg.content}\n"
        else:
            prompt += f"{msg.author.display_name}: {msg.content}\n"
    prompt = f"This is a conversation with an AI. Only the {prompt_size} last messages are used as a prompt.\n\n" + prompt + f"\n AI:"
    #send the request to the api
    debug("Sending request to the api")
    debug(prompt)
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=str(prompt),
        max_tokens=int(max_tokens),
        top_p=1,
        temperature=float(temperature),
        frequency_penalty=float(frequency_penalty),
        presence_penalty=float(presence_penalty),
        stop=[" Human:", " AI:", "AI:", "Human:"]    )
    #send the response
    if response["choices"][0]   ["text"] != "":
        await message.channel.send(response["choices"][0]["text"])
    else:
        await message.channel.send("The AI is not sure what to say (the response was empty)")
        debug("The response was empty")
    debug("The response has been sent")

    #get the message content
    # add a slash command called "say" that sends a message to the channel
@bot.command()
async def transcript(ctx):
#save all the messages in the channel in a txt file and send it
    messages = await ctx.channel.history(limit=None).flatten()
    messages.reverse()
    transcript = ""
    #defer the response
    await ctx.defer()
    for msg in messages:
        if msg.author.bot:
            transcript += f"AI: {msg.content}\n"
        else:
            transcript += f"{msg.author.display_name}: {msg.content}\n"
#save the transcript in a txt file called transcript.txt. If the file already exists, delete it and create a new one
#check if the file exists
    if os.path.exists("transcript.txt"):
        os.remove("transcript.txt")
    f = open("transcript.txt", "w")
    f.write(transcript)
    f.close()
    await ctx.respond(file=discord.File("transcript.txt"))
'''
#these are debug commands and should not be used in production
@bot.slash_command()
async def say(ctx, message: str):
    await ctx.respond("message sent!", ephemeral=True)
    await ctx.send(message)
#add a slash command called "clear" that deletes all the messages in the channel
@bot.slash_command()
async def clear(ctx):
    await ctx.respond("messages deleted!", ephemeral=True)
    return await ctx.channel.purge()
'''
async def reset_uses_count_today():
    await bot.wait_until_ready()
    while not bot.is_closed():
        c.execute("UPDATE data SET uses_count_today = 0")
        conn.commit()
        await asyncio.sleep(86400)
# on startup run the reset_uses_count_today function
bot.loop.create_task(reset_uses_count_today())

#run the bot
# Replace the following with your bot's token
with open("key.txt") as f:
    key = f.read()
bot.run(key)