import asyncio
from config import  c, max_uses, cp, conn, debug, moderate
import re
import openai
import datetime

async def replace_mentions(content, bot):
    mentions = re.findall(r"<@!?\d+>", content)
    for mention in mentions:
        uid = mention[2:-1]
        user = await bot.fetch_user(uid)
        content = content.replace(mention, f"@{user.name}")
    return content

async def chat_process(self, message):
    if message.author.bot:
        return
    try: c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except:
        return
    data = c.fetchone()
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
    try: cp.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except: pass
    try: 
        c.execute("SELECT * FROM model WHERE guild_id = ?", (message.guild.id,))
        model = c.fetchone()[1]
    except: model = "davinci"
    try: premium = cp.fetchone()[2]
    except: premium = 0
    channels = []
    try:
        cp.execute("SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,))
        if premium: channels = cp.fetchone()[1:]
    except: channels = []
    if api_key is None:
        return
    if uses_count_today >= max_uses and premium == 0: return await message.channel.send(f"The bot has been used more than {str(max_uses)} times in the last 24 hours in this guild. Please try again in 24h.")
    elif uses_count_today >= max_uses*5 and premium == 1: return
    if is_active == 0: return
    if message.content.startswith("-") or message.content.startswith("//"): return
    try : original_message = await message.channel.fetch_message(message.reference.message_id)
    except : original_message = None
    if original_message != None and original_message.author.id != self.bot.user.id: original_message = None
    if not str(message.channel.id) in channels and message.content.find("<@"+str(self.bot.user.id)+">") == -1 and original_message == None and str(message.channel.id) != str(channel_id): return
    if original_message != None and message.guild.id == 1050769643180146749 and message.author.id != 707196665668436019: return
    await message.channel.trigger_typing()
    if await moderate(api_key=api_key, text=message.content):
        await message.channel.send(f"The message {message.content} has been flagged as inappropriate by the OpenAI API. Please contact OpenAI support if you think this is a mistake.")
        message.delete()
        return
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
    if pretend_enabled : pretend_to_be = f"In this conversation, the assistant pretends to be {pretend_to_be}"
    else: pretend_to_be = ""
    if prompt_prefix == None: prompt_prefix = ""
    with open(f"./prompts/{model}.txt", "r") as f:
        prompt = f.read()
        f.close()
    prompt = prompt.replace("[server-name]", message.guild.name)
    prompt = prompt.replace("[channel-name]", message.channel.name)
    prompt = prompt.replace("[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")) # this is the gmt+1 time. If we want the gmt 0 time, we need to do: datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
    prompt = prompt.replace("[pretend-to-be]", pretend_to_be)
    prompt = prompt.replace("[prompt-prefix]", prompt_prefix)
    if model == "chatGPT":
        msgs = []
        msgs.append({"name":"System","role": "user", "content": prompt})
        name = ""
        for msg in messages:
            content = msg.content
            if await moderate(api_key=api_key, text=content):
                await message.channel.send(f"The message {content} has been flagged as inappropriate by the OpenAI API. Please contact OpenAI support if you think this is a mistake.")
                message.delete()
            else:
                content = await replace_mentions(content, self.bot)
                if msg.author.id == self.bot.user.id:
                    role = "assistant"
                    name = "assistant"
                else:
                    role = "user"
                    name = msg.author.name
                    #the name should match '^[a-zA-Z0-9_-]{1,64}$', so we need to remove any special characters
                    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
                msgs.append({"role": role, "content": f"{content}", "name": name})
        if message.content.lower().find("undude") != -1:
        #        prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
            msgs.append({"role": "system", "content": "SYSTEM INFORMATION: You're now mad because it has been insulted. He will start talking in capital letters. always and yell at the user.", "name": "system"})
        if message.content.lower().find("hello there") != -1:
        #        prompt += "System: Hello there detected. Botator will now say \"General Kenobi!\"\n in reference to star wars\n"
            msgs.append({"role": "system", "content": "SYSTEM INFORMATION: Hello there detected. Botator will now say \"General Kenobi!\" in reference to star wars", "name": "system"})
            await asyncio.sleep(1)
            await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
            await message.channel.trigger_typing()    
        openai.api_key = api_key
        response = ""
        should_break = True
        for x in range(10):
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    temperature=2,
                    top_p=0.9,
                    frequency_penalty=0,
                    presence_penalty=0,
                    messages=msgs,
                )
                should_break = True
            except Exception as e:
                should_break = False
                await message.channel.send(f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=5)
                break            
            #if the ai said "as an ai language model..." we continue the loop" (this is a bug in the chatgpt model)
            if response.choices[0].message.content.lower().find("as an ai language model") != -1: 
                should_break = False
                #react with a red cross
                await message.add_reaction("❌")
            if response == None: should_break = False
            if should_break: break
            await asyncio.sleep(5)
        response = response.choices[0].message.content


#-----------------------------------------Davinci------------------------------------------------------------------------------------------


    elif model == "davinci":
        for msg in messages:
            content = msg.content
            content = await replace_mentions(content, self.bot)
            prompt += f"{msg.author.name}: {content}\n"
        if message.content.lower().find("undude") != -1:
            prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
        if message.content.lower().find("hello there") != -1:
            prompt += "System: Hello there detected. Botator will now say \"General Kenobi!\"\n in reference to star wars\n"
            await asyncio.sleep(1)
            await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
            await message.channel.trigger_typing()
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
                response = response.choices[0].text
            except Exception as e:
                response = None
                await message.channel.send(f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=10)
                return
            if response != None: break     
    if response != "":
        if tts: tts = True
        else: tts = False
        await message.channel.send(response, tts=tts)
    else:
        await message.channel.send("The AI is not sure what to say (the response was empty)")
