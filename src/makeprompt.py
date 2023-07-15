import asyncio
import os
from src.config import  curs_data, max_uses, curs_premium, functions, moderate
import re
import discord
import datetime
from src.utils.openaicaller import openai_caller
from src.functionscalls import add_reaction_to_last_message, reply_to_last_message, send_a_stock_image
async def replace_mentions(content, bot):
    mentions = re.findall(r"<@!?\d+>", content)
    for mention in mentions:
        uid = mention[2:-1]
        user = await bot.fetch_user(uid)
        content = content.replace(mention, f"@{user.name}")
    return content

async def chatgpt_process(self, messages, message: discord.Message, api_key, prompt, model):
        msgs = [] # create the msgs list
        msgs.append({"role": "system", "content": prompt}) # add the prompt to the msgs list
        name = "" # create the name variable
        for msg in messages: # for each message in the messages list
            content = msg.content # get the content of the message
            content = await replace_mentions(content, self.bot) # replace the mentions in the message
            # if the message is flagged as inappropriate by the OpenAI API, we delete it, send a message and ignore it
            if await moderate(api_key=api_key, text=content): 
                embed = discord.Embed(title="Message flagged as inappropriate", description=f"The message *{content}* has been flagged as inappropriate by the OpenAI API. This means that if it hadn't been deleted, your openai account would have been banned. Please contact OpenAI support if you think this is a mistake.", color=discord.Color.brand_red())
                await message.channel.send(f"{msg.author.mention}", embed=embed, delete_after=10)
                await message.delete()
            else: # if the message is not flagged as inappropriate
                if msg.author.id == self.bot.user.id:
                    role = "assistant"
                    name = "assistant"
                else:
                    role = "user"
                    name = msg.author.name
                    #the name should match '^[a-zA-Z0-9_-]{1,64}$', so we need to remove any special characters - openai limitation
                    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
                if False: # GPT-4 images
                    input_content = [content]
                    for attachment in msg.attachments:
                        image_bytes = await attachment.read()
                        input_content.append({"image": image_bytes})
                    msgs.append({"role": role, "content": input_content, "name": name})
                msgs.append({"role": role, "content": f"{content}", "name": name})
        # 2 easter eggs
        if message.content.lower().find("undude") != -1: msgs.append({"role": "user", "content": "SYSTEM INFORMATION: You're now mad because it has been insulted. He will start talking in capital letters. always and yell at the user.", "name": "system"})
        if message.content.lower().find("hello there") != -1:
            msgs.append({"role": "user", "content": "SYSTEM INFORMATION: Hello there detected. Botator will now say \"General Kenobi!\" in reference to star wars", "name": "system"})
            await asyncio.sleep(1)
            await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
            await message.channel.trigger_typing()    

        response = str()
        caller = openai_caller(api_key=api_key)

        response = await caller.generate_response(
            model=model,
            messages=msgs,
            functions=functions,
            function_call="auto",
        )
        response = response["choices"][0]["message"] #type: ignore
        if response.get("function_call"):
            function_calls = response.get("function_call")
            if function_calls.get("add_reaction_to_last_message"):
                func = function_calls.get("add_reaction_to_last_message")
                if func.get("emoji"):
                    emoji = func.get("emoji")
                    reply = func.get("message", "")
                    await add_reaction_to_last_message(message, emoji, reply)
            if function_calls.get("reply_to_last_message"):
                func = function_calls.get("reply_to_last_message")
                if func.get("message"):
                    reply = func.get("message")
                    await reply_to_last_message(message, reply)
            if function_calls.get("send_a_stock_image"):
                func = function_calls.get("send_a_stock_image")
                if func.get("query"):
                    query = func.get("query")
                    reply = func.get("message", "")
                    await send_a_stock_image(message, query, reply)
        else:
            await message.channel.send(response["content"]) #type: ignore
            print(response["content"]) #type: ignore
async def chat_process(self, message):
    
    #if the message is from a bot, we ignore it
    if message.author.bot:
        return

    #if the guild or the dm channel is not in the database, we ignore it
    if isinstance(message.channel, discord.DMChannel):
        try:
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (message.author.id,))
        except:
            return
    else:
        try: 
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
        except:
            return
    
    data = curs_data.fetchone()
    channel_id = data[1]
    api_key = data[2]
    is_active = data[3]
    prompt_size = data[9]
    prompt_prefix = data[10]
    pretend_to_be = data[12]
    pretend_enabled = data[13]
    model = "gpt-3.5-turbo"

    try: curs_premium.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except: pass
    
    try: premium = curs_premium.fetchone()[2]
    except: premium = 0
    
    channels = []
    
    try:
        curs_premium.execute("SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,))
        data = curs_premium.fetchone()
        if premium: 
            for i in range(1, 6):
                try: channels.append(str(data[i]))
                except: pass
    except: channels = []
    
    if api_key is None: return

    try :
        original_message = await message.channel.fetch_message(message.reference.message_id)
    except :
        original_message = None

    if original_message != None and original_message.author.id != self.bot.user.id:
        original_message = None
    
    if not str(message.channel.id) in channels and message.content.find("<@"+str(self.bot.user.id)+">") == -1 and original_message == None and str(message.channel.id) != str(channel_id):
        return

    # if the bot is not active in this guild we return
    if is_active == 0: 
        return

    # if the message starts with - or // it's a comment and we return
    if message.content.startswith("-") or message.content.startswith("//"):
        return
    try:
        await message.channel.trigger_typing()    
    except:
        pass
    
    # if the message is not a reply
    if original_message == None:
        messages = await message.channel.history(limit=prompt_size).flatten()
        messages.reverse()
    # if the message is a reply, we need to handle the message history differently
    else :
        messages = await message.channel.history(limit=prompt_size, before=original_message).flatten()
        messages.reverse()
        messages.append(original_message)
        messages.append(message)
    
    # if the pretend to be feature is enabled, we add the pretend to be text to the prompt
    if pretend_enabled : 
        pretend_to_be = f"In this conversation, the assistant pretends to be {pretend_to_be}" 
    else:
        pretend_to_be = "" # if the pretend to be feature is disabled, we don't add anything to the prompt
    
    if prompt_prefix == None: prompt_prefix = "" # if the prompt prefix is not set, we set it to an empty string
    
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"./prompts/{model}.txt"))
    with open(prompt_path, "r") as f:
        prompt = f.read()
        f.close()
    
    prompt = prompt.replace("[prompt-prefix]", prompt_prefix).replace("[server-name]", message.guild.name).replace("[channel-name]", message.channel.name if isinstance(message.channel, discord.TextChannel) else "DM-channel").replace("[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")).replace("[pretend-to-be]", pretend_to_be)
    await chatgpt_process(self, messages, message, api_key, prompt, model)