import asyncio
from config import  c, max_uses, cp, conn
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
    prompt = ""
    if model == "chatGPT":
        # we open the chatGPT prompt file located in the ./prompts/chatGPT.txt file
        with open("./prompts/chatGPT.txt", "r") as f:
            prompt = f.read()
            f.close()
        # we replace the variables in the prompt file with the variables we have
        prompt = prompt.replace("[server-name]", message.guild.name)
        prompt = prompt.replace("[channel-name]", message.channel.name)
        prompt = prompt.replace("[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")) # this is the gmt+1 time. If we want the gmt 0 time, we need to do: datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        prompt = prompt.replace("[pretend-to-be]", pretend_to_be)
        prompt = prompt.replace("[prompt-prefix]", prompt_prefix)
        msgs = []
        if prompt_prefix != "": prompt = f"\n{prompt}\n{prompt_prefix}"
        else: prompt = f"\n{prompt}"
        msgs.append({"role": "system", "content": prompt, "name": "system"})
        name = ""
        for msg in messages:
            content = msg.content
            content = await replace_mentions(content, self.bot)
            if msg.author.id == self.bot.user.id:
                role = "assistant"
                name = "assistant"
            else:
                role = "user"
                name = msg.author.name
            msgs.append({"role": role, "content": f"{content}", "name": name})
            print(msgs)
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
        for _ in range(10):
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    max_tokens=int(max_tokens),
                    messages=msgs,
                )
            except Exception as e:
                response = None
                await message.channel.send(f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=10)
                break
            if response != None: break
        response = response.choices[0].message.content


#-----------------------------------------Davinci------------------------------------------------------------------------------------------


    elif model == "davinci":
        prompt = f'''Server name: {message.guild.name}. Channel name: {message.channel.name}.
The assistant is called Botator. {pretend_to_be}. {prompt_prefix} 
Botator is an AI and a regular Discord user. He types casually, uses a lot of emojis in each message. Botator has many niche interests. Botator talks normally and is sentient. Botator is really funny and has a good humor. Botator is intelligent. Botator often uses internet shorthand like "lol" and "bruh". He uses "bruh" a lot.
The date and time is: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC. The assistant can surely tell the time to te users when asked.'''
        prompt = f"{prompt}<|endofprompt|>"
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
