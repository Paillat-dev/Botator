import asyncio
import os
import re
import discord
import datetime
import json

from src.config import curs_data, max_uses, curs_premium, gpt_3_5_turbo_prompt
from src.utils.misc import moderate
from src.utils.openaicaller import openai_caller
from src.functionscalls import (
    add_reaction_to_last_message,
    reply_to_last_message,
    send_a_stock_image,
    create_a_thread,
    send_a_gif,
    send_ascii_art_text,
    send_ascii_art_image,
    functions,
    server_normal_channel_functions,
)


async def replace_mentions(content, bot):
    mentions = re.findall(r"<@!?\d+>", content)
    for mention in mentions:
        uid = mention[2:-1]
        user = await bot.fetch_user(uid)
        content = content.replace(mention, f"@{user.name}")
    return content


async def chatgpt_process(
    self, messages, message: discord.Message, api_key, prompt, model
):
    async def error_call(error=""):
        try:
            if error != "":
                await message.channel.send(
                    f"An error occured: {error}", delete_after=10
                )
            await message.channel.trigger_typing()
        except:
            pass

    msgs = []  # create the msgs list
    msgs.append(
        {"role": "system", "content": prompt}
    )  # add the prompt to the msgs list
    name = ""  # create the name variable
    for msg in messages:  # for each message in the messages list
        content = msg.content  # get the content of the message
        content = await replace_mentions(
            content, self.bot
        )  # replace the mentions in the message
        # if the message is flagged as inappropriate by the OpenAI API, we delete it, send a message and ignore it
        if await moderate(api_key, content, error_call):
            embed = discord.Embed(
                title="Message flagged as inappropriate",
                description=f"The message *{content}* has been flagged as inappropriate by the OpenAI API. This means that if it hadn't been deleted, your openai account would have been banned. Please contact OpenAI support if you think this is a mistake.",
                color=discord.Color.brand_red(),
            )
            await message.channel.send(
                f"{msg.author.mention}", embed=embed, delete_after=10
            )
        else:  # if the message is not flagged as inappropriate
            if msg.author.id == self.bot.user.id:
                role = "assistant"
                name = "assistant"
            else:
                role = "user"
                name = msg.author.name
                # the name should match '^[a-zA-Z0-9_-]{1,64}$', so we need to remove any special characters - openai limitation
                name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
            if False:  # GPT-4 images
                input_content = [content]
                for attachment in msg.attachments:
                    image_bytes = await attachment.read()
                    input_content.append({"image": image_bytes})
                msgs.append({"role": role, "content": input_content, "name": name})
            msgs.append({"role": role, "content": f"{content}", "name": name})
    # 2 easter eggs
    if message.content.lower().find("undude") != -1:
        msgs.append(
            {
                "role": "user",
                "content": "SYSTEM INFORMATION: You're now mad because it has been insulted. He will start talking in capital letters. always and yell at the user.",
                "name": "system",
            }
        )
    if message.content.lower().find("hello there") != -1:
        msgs.append(
            {
                "role": "user",
                "content": 'SYSTEM INFORMATION: Hello there detected. Botator will now say "General Kenobi!" in reference to star wars',
                "name": "system",
            }
        )
        await asyncio.sleep(1)
        await message.channel.send(
            "https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif"
        )
        await message.channel.trigger_typing()

    response = str()
    caller = openai_caller()
    called_functions = (
        functions
        if not isinstance(message.channel, discord.TextChannel)
        else server_normal_channel_functions + functions
    )
    response = await caller.generate_response(
        error_call,
        api_key=api_key,
        model=model,
        messages=msgs,
        functions=called_functions,
        # function_call="auto",
    )
    response = response["choices"][0]["message"]  # type: ignore
    if response.get("function_call"):
        function_call = response.get("function_call")
        name = function_call.get("name", "")
        arguments = function_call.get("arguments", {})
        arguments = json.loads(arguments)
        if name == "add_reaction_to_last_message":
            if arguments.get("emoji"):
                emoji = arguments.get("emoji")
                reply = arguments.get("message", "")
                await add_reaction_to_last_message(message, emoji, reply)
        if name == "reply_to_last_message":
            if arguments.get("message"):
                reply = arguments.get("message")
                await reply_to_last_message(message, reply)
        if name == "send_a_stock_image":
            if arguments.get("query"):
                query = arguments.get("query")
                reply = arguments.get("message", "")
                await send_a_stock_image(message, query, reply)
        if name == "create_a_thread":
            if arguments.get("name") and arguments.get("message"):
                name = arguments.get("name")
                reply = arguments.get("message", "")
                if isinstance(message.channel, discord.TextChannel):
                    await create_a_thread(message.channel, name, reply)
                else:
                    await message.channel.send(
                        "`A server normal text channel only function has been called in a non standard channel. Please retry`",
                        delete_after=10,
                    )
        if name == "send_a_gif":
            if arguments.get("query"):
                query = arguments.get("query")
                reply = arguments.get("message", "")
                limit = arguments.get("limit", 15)
                await send_a_gif(message, query, reply, limit)
        if name == "send_ascii_art_text":
            if arguments.get("text"):
                text = arguments.get("text")
                font = arguments.get("font", "standard")
                reply = arguments.get("message", "")
                await send_ascii_art_text(message, text, font, reply)
        if name == "send_ascii_art_image":
            if arguments.get("query"):
                query = arguments.get("query")
                reply = arguments.get("message", "")
                await send_ascii_art_image(message, query, reply)
        if name == "":
            await message.channel.send(
                "The function call is empty. Please retry.", delete_after=10
            )
    else:
        content = response.get("content", "")
        while len(content) != 0:
            if len(content) > 2000:
                await message.channel.send(content[:2000])
                content = content[2000:]
            else:
                await message.channel.send(content)
                content = ""


async def chat_process(self, message):
    if message.author.id == self.bot.user.id:
        return

    if isinstance(message.channel, discord.DMChannel):
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (message.author.id,)
            )
        except:
            return
    else:
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (message.guild.id,)
            )
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

    try:
        curs_premium.execute(
            "SELECT * FROM data WHERE guild_id = ?", (message.guild.id,)
        )
    except:
        pass

    try:
        premium = curs_premium.fetchone()[2]
    except:
        premium = 0

    channels = []

    try:
        curs_premium.execute(
            "SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,)
        )
        data = curs_premium.fetchone()
        if premium:
            for i in range(1, 6):
                try:
                    channels.append(str(data[i]))
                except:
                    pass
    except:
        channels = []

    if api_key is None:
        return

    try:
        original_message = await message.channel.fetch_message(
            message.reference.message_id
        )
    except:
        original_message = None

    if original_message != None and original_message.author.id != self.bot.user.id:
        original_message = None
    is_bots_thread = False
    if isinstance(message.channel, discord.Thread):
        if message.channel.owner_id == self.bot.user.id:
            is_bots_thread = True
    if (
        not str(message.channel.id) in channels
        and message.content.find("<@" + str(self.bot.user.id) + ">") == -1
        and original_message == None
        and str(message.channel.id) != str(channel_id)
        and not is_bots_thread
    ):
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
    else:
        messages = await message.channel.history(
            limit=prompt_size, before=original_message
        ).flatten()
        messages.reverse()
        messages.append(original_message)
        messages.append(message)

    # if the pretend to be feature is enabled, we add the pretend to be text to the prompt
    if pretend_enabled:
        pretend_to_be = (
            f"In this conversation, the assistant pretends to be {pretend_to_be}"
        )
    else:
        pretend_to_be = ""  # if the pretend to be feature is disabled, we don't add anything to the prompt

    if prompt_prefix == None:
        prompt_prefix = (
            ""  # if the prompt prefix is not set, we set it to an empty string
        )

    prompt_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"./prompts/{model}.txt")
    )
    prompt = gpt_3_5_turbo_prompt[:] # copy the prompt but to dnot reference it
    if not isinstance(message.channel, discord.DMChannel):        
        prompt = (
            prompt.replace("[prompt-prefix]", prompt_prefix)
            .replace("[server-name]", message.guild.name)
            .replace(
                "[channel-name]",
                message.channel.name
            )
            .replace(
                "[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            )
            .replace("[pretend-to-be]", pretend_to_be)
        )
    else:
        prompt = (
            prompt.replace("[prompt-prefix]", prompt_prefix)
            .replace("[server-name]", "DM-channel")
            .replace(
                "[channel-name]",
                "DM-channel"
            )
            .replace(
                "[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            )
            .replace("[pretend-to-be]", pretend_to_be)
        )
    await chatgpt_process(self, messages, message, api_key, prompt, model)
