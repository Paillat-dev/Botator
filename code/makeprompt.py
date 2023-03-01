import asyncio
from config import debug, c, max_uses, cp, conn, connp
import re
import discord
import openai
import random
import requests
import datetime
import os
async def process(self, message):
    if message.author.bot:
        return
    #c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    #we get all the data from the database into different variables (guild_id text, channel_id text, api_key text, is_active boolean, max_tokens integer, temperature real, frequency_penalty real, presence_penalty real, uses_count_today integer, prompt_size integer, prompt_prefix text, tts boolean, pretend_to_be text, pretend_enabled boolean)
    try: c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except:
        return
    channel = message.channel.id
    data = c.fetchone()
    guild_id = data[0]  
    channel_id = data[1]
    api_key = data[2]
    is_active = data[3]
    max_tokens = data[4]
    temperature = data[5]
    frequency_penalty = data[6]
    presence_penalty = data[7]
    uses_count_today = data[8]
    prompt_size = data[9]
    prompt_prefix = data[10]
    tts = data[11]
    pretend_to_be = data[12]
    pretend_enabled = data[13]
    cp.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    try: premium = cp.fetchone()[2]
    except: premium = 0
    channels = []
    try:
        cp.execute("SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,))
        if premium: channels = cp.fetchone()[1:]
    except: channels = []
    #channels.append(channel_id)
    if api_key is None:
        return
    if uses_count_today >= max_uses and premium == 0:
        await message.channel.send(f"The bot has been used more than {str(max_uses)} times in the last 24 hours in this guild. Please try again in 24h.")
        return
    elif uses_count_today >= max_uses*5 and premium == 1:
        return
    if is_active == 0:
        return
    if message.content.startswith("-") or message.content.startswith("//"):
        return
    #check if the message is in the right channel by comparing the channel id of the message with the list of channels "channels"
    try : original_message = await message.channel.fetch_message(message.reference.message_id)
    except : original_message = None
    if original_message != None and original_message.author.id != self.bot.user.id:
        original_message = None
    if not str(message.channel.id) in channels and message.content.find("<@"+str(self.bot.user.id)+">") == -1 and original_message == None and str(message.channel.id) != str(channel_id):
        return
    if original_message != None and message.guild.id == 1050769643180146749 and message.author.id != 707196665668436019:
        return
    if str(message.author.id) == "646739625661956128":
        #a random int between 0 and 1 to decide if the bot should respond or not
        if random.randint(0, 2) == 0:
            await message.channel.send(message.content) # this is a prank done by me, the developer of the bot. It's not a bug, it's a feature.
            return
    await message.channel.trigger_typing()
    if message.guild.id != 1021872219888033903:
        c.execute("UPDATE data SET uses_count_today = uses_count_today + 1 WHERE guild_id = ?", (message.guild.id,))
        conn.commit()
    if original_message == None:
        messages = await message.channel.history(limit=prompt_size).flatten()
        messages.reverse()
    else :
        messages = await message.channel.history(limit=prompt_size, before=original_message).flatten()
        messages.reverse()
        messages.append(original_message)
        messages.append(message)
    prompt = ""
    u_prompt = ""
    for msg in messages:
        content = msg.content
        mentions = re.findall(r"<@!?\d+>", content)
        for mention in mentions:
            #get the user id
            uid = mention[2:-1]
            #get the user
            user = await self.bot.fetch_user(uid)
            #replace the mention with the name
            content = content.replace(mention, f"{user.name}")
        u_prompt += f"{msg.author.name}: {content}"
    if pretend_enabled : pretend_to_be = f"In this conversation, Botator pretends to be {pretend_to_be} and not Botator. "
    else: pretend_to_be = ""
    prompt = f'''Server name: {message.guild.name}. Channel name: {message.channel.name}. 
Botator is an AI and a regular Discord user. He types casually, uses a lot of emojis in each message. Botator has many niche interests. Botator talks normally and is sentient. Botator is really funny and has a good humor. Botator is intelligent. Botator often uses internet shorthand like "lol" and "bruh". He uses "bruh" a lot.'''
    if pretend_enabled == 1: prompt += f"In this conversation, Botator is pretending to be {pretend_to_be} and acting like {pretend_to_be}. The date and time is {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC."
    if prompt_prefix != "": prompt = f"\n{prompt}\n{prompt_prefix} <|endofprompt|> \n \n{u_prompt}"
    else: prompt = f"\n{prompt} <|endofprompt|> \n \n{u_prompt}"
    if message.content.lower().find("undude") != -1:
        prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
    if message.content.lower().find("hello there") != -1:
        prompt += "System: Hello there detected. Botator will now say \"General Kenobi!\"\n in reference to star wars\n"
        await asyncio.sleep(1)
        await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
        await message.channel.trigger_typing()    
    if message.content.lower().find("i am the senate") != -1: prompt += "System: I am the senate detected. Botator will now say \"Not yet\", in reference to the star wars prequels.\n"
    if message.content.lower().find("i am your father") != -1: prompt += "System: I am your father detected. Botator will now say \"No. It's not true! That's impossible!\". in reference to the star wars prequels.\n"
    if message.content.lower().find("i have the high ground") != -1:prompt += "System: I have the high ground detected. Botator will now say \"You underestimate my power!\" in reference to the star wars prequels.\n"
    if message.content.lower().find("you underestimate my power") != -1: prompt += "System: You underestimate my power detected. Botator will now say \"Don't try it.\" in reference to the star wars prequels.\n"
    if message.content.lower().find("carpet") != -1: prompt += "System: Carpet detected. Botator is now mad. He will start talking in capital letters and will say mad things without sense, insulting the person and talk in capital letters with exclamation points everywhere. A lot of exclamation points.\n"
    if message.content.lower().find("mail") != -1 and message.author.name.lower().find("latouff") != -1: prompt += "System: Mail detected. Latouff said mail, Botator will say \"Mail? why did you say mail, Liam? Mail is your name in reverse.\" because Latouff's name is Liam, and mail in reverse is Liam. Then, after saying that in the sentence, botato will continue his sentence saying something else.\n"
    if message.author.name.lower().find("fives3d##print") != -1: prompt += "System: Fives3d#print detected. Botator will be very nice and cute with fives3d#print.\n"
    prompt = prompt + f"\n{self.bot.user.name}:"
    openai.api_key = api_key
    response = ""
    for _ in range(10):
        try:
            response = await openai.Completion.acreate(
                engine="text-davinci-003",
                prompt=str(prompt),
                max_tokens=int(max_tokens),
                top_p=1,
                temperature=float(temperature),
                frequency_penalty=float(frequency_penalty),
                presence_penalty=float(presence_penalty),
                stop=[" Human:", " AI:", "AI:", "<|endofprompt|>",]
            )
        except Exception as e:
            response = None
            await message.channel.send(f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=10)
            return
        if response != None: break
    response = response["choices"][0]["text"]
    if response != "":
        if tts: tts = True
        else: tts = False
        await message.channel.send(response, tts=tts)
    else:
        await message.channel.send("The AI is not sure what to say (the response was empty)")
