import openai # pip install openai
import discord # pip install pycord
from discord import File, Intents # pip install pycord
import logging # pip install logging
import sqlite3 # pip install sqlite3
#set the debug mode to the maximum
logging.basicConfig(level=logging.INFO)
def debug(message):
    logging.info(message)

#create a database called "database.db" if the database does not exist, else connect to it
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create table called "data" if it does not exist with the following columns: guild_id, channel_id, api_key, is_active
c.execute('''CREATE TABLE IF NOT EXISTS data (guild_id text, channel_id text, api_key text, is_active boolean)''')
Intents =discord.Intents.all() # enable all intents
Intents.members = True
bot = discord.Bot(intents=Intents.all())
#create a command called "setchannel"
@bot.command()
async def setchannel(ctx, channel: discord.TextChannel):
    # Check if the bot has the "Manage Channels" permission
    if ctx.author.guild_permissions.manage_channels:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            # Insert the channel id into the database
            c.execute("INSERT INTO data VALUES (?, ?, ?, ?)", (ctx.guild.id, channel.id, None, False))
            conn.commit()
            await ctx.respond("Channel set!",ephemeral=True)
        else:
            await ctx.respond("Channel already set!",ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!",ephemeral=True)
#create a command called "setkey"
@bot.command()
async def setkey(ctx, key):
    # Check if the bot has the "Manage Channels" permission
    if ctx.author.guild_permissions.manage_channels:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is not None:
            # Insert the api key into the database
            c.execute("UPDATE data SET api_key = ? WHERE guild_id = ?", (key, ctx.guild.id))
            conn.commit()
            await ctx.respond("Key set!",ephemeral=True)
        else:
            await ctx.respond("Channel not set!",ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!",ephemeral=True)
#create a command called "enable"
@bot.command()
async def enable(ctx):
    # Check if the bot has the "Manage Channels" permission
    if ctx.author.guild_permissions.manage_channels:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is not None:
            # Check if the api key is already set
            c.execute("SELECT api_key FROM data WHERE guild_id = ?", (ctx.guild.id,))
            if c.fetchone() is not None:
                # Set is_active to True
                c.execute("UPDATE data SET is_active = ? WHERE guild_id = ?", (True, ctx.guild.id))
                conn.commit()
                await ctx.respond("Enabled!", ephemeral=True)
            else:
                await ctx.respond("Key not set!", ephemeral=True)
        else:
            await ctx.respond("Channel not set!", ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!", ephemeral=True)
#create a command called "disable"
@bot.command()
async def disable(ctx):
    # Check if the bot has the "Manage Channels" permission
    if ctx.author.guild_permissions.manage_channels:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is not None:
            # Check if the api key is already set
            c.execute("SELECT api_key FROM data WHERE guild_id = ?", (ctx.guild.id,))
            if c.fetchone() is not None:
                # Set is_active to false
                c.execute("UPDATE data SET is_active = ? WHERE guild_id = ?", (False, ctx.guild.id))
                conn.commit()
                await ctx.respond("Disabled!", ephemeral=True)
            else:
                await ctx.respond("Key not set!", ephemeral=True)
        else:
            await ctx.respond("Channel not set!", ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!", ephemeral=True)
#create a command called "delete" to delete the channel and api key from the database
@bot.command()
async def delete(ctx): 
    # Check if the bot has the "Manage Channels" permission
    if ctx.author.guild_permissions.manage_channels:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is not None:
            # Delete the channel and api key from the database
            c.execute("DELETE FROM data WHERE guild_id = ?", (ctx.guild.id,))
            conn.commit()
            await ctx.respond("Deleted!", ephemeral=True)
        else:
            await ctx.respond("Channel not set!", ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!", ephemeral=True)
        #create a command called "info" to get the channel and api key from the database
@bot.command()
async def info(ctx):
    # Check if the bot has the "administrator" permission
    if ctx.author.guild_permissions.administrator:
        # Check if the channel is already set
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is not None:
            # Get the channel and api key from the database
            c.execute("SELECT channel_id, api_key FROM data WHERE guild_id = ?", (ctx.guild.id,))
            channel_id, api_key = c.fetchone()
            await ctx.respond(f"Channel: {channel_id}, api key: {api_key}", ephemeral=True)
        else:
            await ctx.respond("Channel not set!", ephemeral=True)
    else:
        await ctx.respond("You do not have the permission to do that!", ephemeral=True)
# when a message is sent in a channel, check if the channel is in the database for the guild, and if it is,  and if it is not, check if the channel is active, and if it is, check if the user is a bot, and if it is not, send the message to openai with the 5 last messages from the channel as the prompt
@bot.event
async def on_message(message):
    debug(message)
    # Check if the channel is in the database for the guild and if the message has been sent in that channel
    c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (message.guild.id,))
    channel = c.fetchone()
    debug(channel[0])
    debug(message.channel.id)
    if channel is not None and str(message.channel.id) == str(channel[0]):
        debug("Channel is in database")
        # Check if the channel is active
        c.execute("SELECT is_active FROM data WHERE guild_id = ?", (message.guild.id,))
        if c.fetchone() == (True,):
            debug("Channel is active")
            # Check if the user is a bot
            if not message.author.bot:
                debug("User is not a bot")
                # Get the api key from the database
                c.execute("SELECT api_key FROM data WHERE guild_id = ?", (message.guild.id,))
                api_key = c.fetchone()[0]
                # Get the 5 last messages from the channel
                messages = await message.channel.history(limit=5).flatten()
                # Create the prompt with the 5 last messages and the message sent by the user goint at the line after each message, adding HUMAN: before the messages taht were not sent by the bot and AI: before the messages that were sent by the bot
                prompt = ""
                for m in messages:
                    #add at the beginning of the prompt and not at the end to have the messages in the right order 
                    if m.author.bot:
                        prompt = f"AI: {m.content}\n" + prompt
                    else:
                        prompt = m.author.display_name + ": " + m.content + "\n" + prompt
                        #prompt = f"HUMAN: {m.content}\n" + prompt
                #add AI: at the end of the prompt
                prompt += "AI:"
                prompt = "This is a conversation with an AI. Only the last 5 messages are taken as a prompt. \n \n" + prompt
                debug(prompt)
#                prompt += f"HUMAN: {message.content}"
                #set the api key
                openai.api_key = api_key
                # Send the prompt to openai
                response = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=prompt,
                    temperature=0.9,
                    max_tokens=512,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                    stop=["\n", " Human:", " AI:"]
                )
                # Send the response to the channel
                if response["choices"][0]   ["text"] != "":
                    await message.channel.send(response["choices"][0]["text"])
                else:
                    # If the response is empty, send a message saying that the response is empty
                    await message.channel.send("I don't know what to say (response is empty)")
# add a slash command called "say" that sends a message to the channel
@bot.slash_command()
async def say(ctx, message: str):
    await ctx.respond("message sent!", ephemeral=True)
    await ctx.send(message)
#add a slash command called "clear" that deletes all the messages in the channel
@bot.slash_command()
async def clear(ctx):
    await ctx.respond("messages deleted!", ephemeral=True)
    return await ctx.channel.purge()

#run the bot
# Replace the following with your bot's token
bot.run("MTA0NjA1MTg3NTc1NTEzNDk5Ng.G_-SJl.GmGltmsIp6lD_HsaiS0XI4v48lEhTkUXtGcP_0")
