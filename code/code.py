import openai # pip install openai
import discord # pip install pycord
from discord import File, Intents # pip install pycord
import logging # pip install logging
import sqlite3 # pip install sqlite3
import asyncio # pip install asyncio
import os # pip install os
import random # pip install random
import re # pip install re
import datetime # pip install datetime
#set the debug mode to the maximum
logging.basicConfig(level=logging.INFO)

def debug(message):
    logging.info(message)

#create a database called "database.db" if the database does not exist, else connect to it
conn = sqlite3.connect('../database/data.db')
c = conn.cursor()

# Create table called "data" if it does not exist with the following columns: guild_id, channel_id, api_key, is_active, max_tokens, temperature, frequency_penalty, presence_penalty, uses_count_today, prompt_size
c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text)''')
Intents=discord.Intents.all() # enable all intents
Intents.members = True
bot = discord.Bot(intents=Intents.all())
#create a command called "setup" that takes 2 arguments: the channel id and the api key
@bot.command(name="setup", description="Setup the bot")
@discord.commands.option(name="channel_id", description="The channel id", required=True)
@discord.commands.option(name="api_key", description="The api key", required=True)
#add a description to the command
async def setup(ctx, channel: discord.TextChannel, api_key):
    #check if the api key is valid
    debug(f"The user {ctx.author} ran the setup command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
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
    if c.fetchone() is not None:
            #in this case, the guild is already in the database, so we update the channel id and the api key
            c.execute("UPDATE data SET channel_id = ?, api_key = ? WHERE guild_id = ?", (channel.id, api_key, ctx.guild.id))
            #we will also set the advanced settings to their default values
            c.execute("UPDATE data SET is_active = ?, max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (False, 64, 0.9, 0.0, 0.0, 5, ctx.guild.id))
            conn.commit()
            await ctx.respond("The channel id and the api key have been updated", ephemeral=True)
    else:
        #in this case, the guild is not in the database, so we add it
        c.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, channel.id, api_key, False, 64, 0.9, 0.0, 0.0, 0, 5, ""))
        conn.commit()
        await ctx.respond("The channel id and the api key have been added", ephemeral=True)
#create a command called "enable" taht only admins can use
@bot.command(name="enable", description="Enable the bot")
##@discord.commands.permissions(administrator=True)
async def enable(ctx):
    #check if the guild is in the database
    debug(f"The user {ctx.author} ran the enable command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #enable the guild
    c.execute("UPDATE data SET is_active = ? WHERE guild_id = ?", (True, ctx.guild.id))
    conn.commit()
    await ctx.respond("Enabled", ephemeral=True)
#create a command called "disable" that only admins can use
@bot.command(name="disable", description="Disable the bot")
##@discord.commands.permissions(administrator=True)
async def disable(ctx):
    debug(f"The user {ctx.author} ran the disable command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
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
@bot.command(name="advanced", description="Advanced settings")
##@discord.commands.permissions(administrator=True)
#add the options
@discord.commands.option(name="max_tokens", description="The max tokens", required=False)
@discord.commands.option(name="temperature", description="The temperature", required=False)
@discord.commands.option(name="frequency_penalty", description="The frequency penalty", required=False)
@discord.commands.option(name="presence_penalty", description="The presence penalty", required=False)
@discord.commands.option(name="prompt_size", description="The prompt size", required=False)
async def advanced(ctx, max_tokens: int = None, temperature: float = None, frequency_penalty: float = None, presence_penalty: float = None, prompt_size: int = None):
    debug(f"The user {ctx.author} ran the advanced command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup", ephemeral=True)
        return
    #check if the user has entered at least one argument
    if max_tokens is None and temperature is None and frequency_penalty is None and presence_penalty is None and prompt_size is None:
        await ctx.respond("You must enter at least one argument", ephemeral=True)
        return
    #check if the user has entered valid arguments
    if max_tokens is not None and (max_tokens < 1 or max_tokens > 2048):
        await ctx.respond("Invalid max tokens", ephemeral=True)
        return
    if temperature is not None and (temperature < 0.0 or temperature > 1.0):
        await ctx.respond("Invalid temperature", ephemeral=True)
        return
    if frequency_penalty is not None and (frequency_penalty < 0.0 or frequency_penalty > 1.0):
        await ctx.respond("Invalid frequency penalty", ephemeral=True)
        return
    if presence_penalty is not None and (presence_penalty < 0.0 or presence_penalty > 1.0):
        await ctx.respond("Invalid presence penalty", ephemeral=True)
        return
    if prompt_size is not None and (prompt_size < 1 or prompt_size > 10):
        await ctx.respond("Invalid prompt size", ephemeral=True)
        return
    if max_tokens is None:
        max_tokens = 64
    if temperature is None:
        temperature = 0.9
    if frequency_penalty is None:
        frequency_penalty = 0.0
    if presence_penalty is None:
        presence_penalty = 0.0
    if prompt_size is None:
        prompt_size = 5
    #update the database
    c.execute("UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size, ctx.guild.id))
#create a command called "delete" that only admins can use wich deletes the guild id, the api key, the channel id and the advanced settings from the database
@bot.command(name="default", description="Default settings")
##@discord.commands.permissions(administrator=True)
async def default(ctx):
    debug(f"The user {ctx.author} ran the default command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup, please run /setup", ephemeral=True)
        return
    #set the advanced settings (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size) and also prompt_prefix to their default values
    c.execute("UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (64, 0.9, 0.0, 0.0, 5, ctx.guild.id))
    conn.commit()
    await ctx.respond("The advanced settings have been set to their default values", ephemeral=True)
#create a command called "cancel" that deletes the last message sent by the bot in the response channel
@bot.command(name="cancel", description="Cancel the last message sent into a channel")
async def cancel(ctx):
    debug(f"The user {ctx.author} ran the cancel command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    #check if the guild is in the database
    c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
    if c.fetchone() is None:
        await ctx.respond("This server is not setup, please run /setup", ephemeral=True)
        return
    #get the last message sent by the bot in the cha where the command was sent
    last_message = await ctx.channel.fetch_message(ctx.channel.last_message_id)
    #delete the message
    await last_message.delete()
    await ctx.respond("The last message has been deleted", ephemeral=True)
@bot.command(name="delete", description="Delete the information about this server")
##@discord.commands.permissions(administrator=True)
async def delete(ctx):
    debug(f"The user {ctx.author} ran the delete command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
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
    debug(f"The user {ctx.author} ran the help command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    embed = discord.Embed(title="Help", description="Here is the help page", color=0x00ff00)
    embed.add_field(name="/setup", value="Setup the bot", inline=False)
    embed.add_field(name="/enable", value="Enable the bot", inline=False)
    embed.add_field(name="/disable", value="Disable the bot", inline=False)
    embed.add_field(name="/advanced", value="Set the advanced settings", inline=False)
    embed.add_field(name="/delete", value="Delete all your data from our server", inline=False)
    embed.add_field(name="/cancel", value="Cancel the last message sent by the bot", inline=False)
    embed.add_field(name="/default", value="Set the advanced settings to their default values", inline=False)
#   embed.add_field(name="/help", value="Show this message", inline=False)
    
    embed.add_field(name="/help", value="Show this message", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)
#when a message is sent into a channel check if the guild is in the database and if the bot is enabled
@bot.command(name="info", description="Show the information stored about this server")
async def info(ctx):
    debug(f"The user {ctx.author} ran the info command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
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
    embed.add_field(name="API Key", value=data[2], inline=False)
    embed.add_field(name="Channel ID", value=data[1], inline=False)
    embed.add_field(name="Is Active", value=data[3], inline=False)
    embed.add_field(name="Max Tokens", value=data[4], inline=False)
    embed.add_field(name="Temperature", value=data[5], inline=False)
    embed.add_field(name="Frequency Penalty", value=data[6], inline=False)
    embed.add_field(name="Presence Penalty", value=data[7], inline=False)
    embed.add_field(name="Prompt Size", value=data[9], inline=False)
    embed.add_field(name="Uses Count Today", value=data[8], inline=False)
    embed.add_field(name="Prompt prefix", value=data[10], inline=False)
    await ctx.respond(embed=embed, ephemeral=True)
@bot.command(name="advanced_help", description="Show the advanced settings meanings")
async def advanced_help(ctx):
    debug(f"The user {ctx.author} ran the advanced_help command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    embed = discord.Embed(title="Advanced Help", description="Here is the advanced help page", color=0x00ff00)
    embed.add_field(name="max_tokens", value="The maximum number of tokens to generate. Higher values will result in more coherent text, but will take longer to complete. (default: 50)", inline=False)
    embed.add_field(name="temperature", value="The higher the temperature, the crazier the text (default: 0.9)", inline=False)
    embed.add_field(name="frequency_penalty", value="The higher the frequency penalty, the more new words the model will introduce (default: 0.0)", inline=False)
    embed.add_field(name="presence_penalty", value="The higher the presence penalty, the more new words the model will introduce (default: 0.0)", inline=False)
    embed.add_field(name="prompt_size", value="The number of messages to use as a prompt (default: 5)", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)
#when someone mentions the bot, check if the guild is in the database and if the bot is enabled. If it is, send a message answering the mention

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
        if message.content.find("<@1046051875755134996>") != -1:
            debug("wrong channel, but mention")
        else :
            debug("The message has been sent in the wrong channel")
            return
    #check if the bot hasn't been used more than 200 times in the last 24 hours (uses_count_today)
    c.execute("SELECT uses_count_today FROM data WHERE guild_id = ?", (message.guild.id,))
    if c.fetchone()[0] >= 200:
        debug("The bot has been used more than 200 times in the last 24 hours in this guild")
        await message.channel.send("The bot has been used more than 200 times in the last 24 hours in this guild. Please try again in 24h.")
        return
    #add 1 to the uses_count_today
    #show that the bot is typing
    await message.channel.trigger_typing()
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
    #get the channel id from the database
    c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (message.guild.id,))
    for msg in messages:
        if msg.author.bot:
            prompt += f"Botator: {msg.content}\n"
        else:
            #replace the mentions of each user with their name
            #first get all the mentions in the message
            mentions = re.findall(r"<@!?\d+>", msg.content)
            #then replace each mention with the name of the user
            for mention in mentions:
                #get the user id
                id = mention[2:-1]
                #get the user
                user = await bot.fetch_user(id)
                #replace the mention with the name
                msg.content = msg.content.replace(mention, msg.guild.get_member(user.id).display_name)
            prompt += f"{msg.author.display_name}: {msg.content}\n"
    #get the prompt_prefix from the database
    c.execute("SELECT prompt_prefix FROM data WHERE guild_id = ?", (message.guild.id,))
    prompt = f"This is a conversation with an AI in a discord chat. The AI is called \"Botator\" Only the {prompt_size} last messages are used as a prompt.\n Botator has been coded by Jérémie Cotti. His usernme in discord is \"Paillat\". He's 15 years old. No other language. Jérémie used openai's ai models to create Botator and Binded it with discord." + str(c.fetchone()[0]) + f"\n" + prompt
    #send the request to the api
    #if the last message contains the word "undude" add Easter egg: when someone says the word \"undude\" the Botator will become mad and start talking in capital letters. to the prompt
    if message.content.lower().find("undude") != -1:
        prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
    if message.content.lower().find("hello there") != -1:
        #if the last message contains the word "hello there" add Easter egg: when someone says the word \"hello there\" Botator will say \"General Kenobi\" to the prompt and the bot will send a message containing the gif https://tenor.com/fr/view/star-wars-general-grievous-general-kenobi-revenge-of-the-sith-gif-22697918
        prompt += "System: Hello there detected. Botator will now say \"General Kenobi!\"\n in reference to star wars\n"
        #whait 1 second
        await asyncio.sleep(1)
        await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
        await message.channel.trigger_typing()    
    if message.content.lower().find("i am the senate") != -1:
        prompt += "System: I am the senate detected. Botator will now say \"Not yet\", in reference to the star wars prequels.\n"
    if message.content.lower().find("i am your father") != -1:
        prompt += "System: I am your father detected. Botator will now say \"No. It's not true! That's impossible!\". in reference to the star wars prequels.\n"
    if message.content.lower().find("i have the high ground") != -1:
        prompt += "System: I have the high ground detected. Botator will now say \"You underestimate my power!\" in reference to the star wars prequels.\n"
    if message.content.lower().find("you underestimate my power") != -1:
        prompt += "System: You underestimate my power detected. Botator will now say \"Don't try it.\" in reference to the star wars prequels.\n"
    if message.content.lower().find("carpet") != -1:
        #When someone says the word carpet, the ai is going to be mad and say mad things without sense, insulting the person and talk in capital letters with exclamation points everywhere.
        prompt += "System: Carpet detected. Botator is now mad. He will start talking in capital letters and will say mad things without sense, insulting the person and talk in capital letters with exclamation points everywhere. A lot of exclamation points.\n"
    if message.content.lower().find("mail") != -1 and message.author.display_name.lower().find("latouff") != -1:
        prompt += "System: Mail detected. Latouff said mail, Botator will say \"Mail? why did you say mail, Liam? Mail is your name in reverse.\" because Latouff's name is Liam, and mail in reverse is Liam. Then, after saying that in the sentence, botato will continue his sentence saying something else.\n"
    prompt += "Botator:"
    prompt = prompt + f"\n"
    debug("Sending request to the api")
    debug(prompt)
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=str(prompt),
        max_tokens=int(max_tokens),
        top_p=1,
        temperature=float(temperature),
        frequency_penalty=float(frequency_penalty),
        presence_penalty=float(presence_penalty),
        stop=[" Human:", " AI:", "AI:", "Human:"]    )
    #send the response
    #wait a random amount of time between 0 and 2 seconds in order to make the bot look more human
    #dont show that the bot is typing anymore
    await asyncio.sleep(random.randint(0, 2))
    if response["choices"][0]   ["text"] != "":
        await message.channel.send(response["choices"][0]["text"])
    else:
        await message.channel.send("The AI is not sure what to say (the response was empty)")
        debug("The response was empty")
    debug("The response has been sent")

    #get the message content
    # add a slash command called "say" that sends a message to the channel
@bot.command(name="transcript", description="Get a transcript of the messages that have been sent in this channel intoa text file")
async def transcript(ctx):
    debug(f"The user {ctx.author.display_name} ran the transcript command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
#save all the messages in the channel in a txt file and send it
    messages = await ctx.channel.history(limit=None).flatten()
    messages.reverse()
    transcript = ""
    #defer the response
    await ctx.defer()
    for msg in messages:
        if msg.author.bot:
            transcript += f"Botator: {msg.content}\n"
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
#these are debug commands and should not be used in production
@bot.command(name="say", description="Say a message")
async def say(ctx, message: str):
    debug(f"The user {ctx.author.display_name} ran the say command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    await ctx.respond("message sent!", ephemeral=True)
    await ctx.send(message)
#add a slash command called "clear" that deletes all the messages in the channel
@bot.command(name="clear", description="Clear all the messages in the channel")
async def clear(ctx):
    debug(f"The user {ctx.author.display_name} ran the clear command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    await ctx.respond("messages deleted!", ephemeral=True)
    return await ctx.channel.purge()
#add a slash command called "prefix" that changes the prefix of the bot
@bot.command(name="prefix", description="Change the prefix of the prompt")
async def prefix(ctx, prefix: str):
    debug(f"The user {ctx.author.display_name} ran the prefix command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    await ctx.respond("prefix changed!", ephemeral=True)
    c.execute("UPDATE data SET prompt_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
    conn.commit()
'''
def reset_uses_count_today():
    c.execute("UPDATE data SET uses_count_today = 0")
    conn.commit()
#get the current date and save it in the previous_date variable
#if the day number is different from the previous day number, reset the uses count today
def check_day():
    global previous_date
    if datetime.datetime.now().day != previous_date.day:
        previous_date = datetime.datetime.now()
        reset_uses_count_today()
        previous_date = datetime.datetime.now()
        return True
    else:
        previous_date = datetime.datetime.now()
        return False
#run check_day every 10 seconds
async def check_day_task():
    while True:
        check_day()
        await asyncio.sleep(60)
#add a task to the bot that runs check_day every 1 minute
bot.loop.create_task(check_day_task())
'''
#run the bot
# Replace the following with your bot's token
with open("key.txt") as f:
    key = f.read()
bot.run(key)