import asyncio
from config import c, max_uses, cp, conn, debug, moderate
import vision_processing
import re
import discord
import datetime
import openai
import emoji  # pip install emoji
import os


async def replace_mentions(content, bot):
    mentions = re.findall(r"<@!?\d+>", content)
    for mention in mentions:
        uid = mention[2:-1]
        user = await bot.fetch_user(uid)
        content = content.replace(mention, f"@{user.name}")
    return content


async def extract_emoji(string):
    # Match any character that is jus after a "+"
    pattern = r"(?<=\+)."
    # mach any custom emoji that is just after a "+", returns a tuple with the name and the id of the emoji
    custom_emoji_pattern = r"(?<=\+)<:(.+):(\d+)>"
    # now we match the pattern with the string
    matches = re.findall(pattern, string)
    custom_emoji_matches = re.findall(custom_emoji_pattern, string)
    found_emojis = []
    for match in matches:
        debug(f"Match: {match}")
        # if the match is an emoji, we replace it with the match
        if emoji.emoji_count(match) > 0:
            debug(f"Found emoji: {match}")
            found_emojis.append(match)
            debug(f"Sting before: {string}")
            string = string.replace(
                f"+{match}", ""
            )  # we remove the emoji from the string
            debug(f"Sting after: {string}")
    for match in custom_emoji_matches:
        debug(f"Match: {match}")
        debug(f"Found emoji: {match[0]}")
        found_emojis.append(match[1])
        string = string.replace(f"+<:{match[0]}:{match[1]}>", "")
    return found_emojis, string


async def chat_process(self, message):
    if message.author.bot:
        return
    try:
        c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
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
    images_limit_reached = False
    try:
        cp.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except:
        pass
    try:
        c.execute(
            "SELECT * FROM model WHERE guild_id = ?", (message.guild.id,)
        )  # get the model in the database
        model = c.fetchone()[1]
    except:
        model = "chatGPT"

    try:
        premium = cp.fetchone()[2]  # get the premium status of the guild
    except:
        premium = 0  # if the guild is not in the database, it's not premium

    try:
        c.execute(
            "SELECT * FROM images WHERE guild_id = ?", (message.guild.id,)
        )  # get the images setting in the database
        data = c.fetchone()
    except:
        data = None
    if data is None:
        data = [message.guild.id, 0, 0]
    images_usage = data[1]
    images_enabled = data[2]
    channels = []
    if message.guild.id == 1050769643180146749:
        images_usage = 0  # if the guild is the support server, we set the images usage to 0, so the bot can be used as much as possible
    try:
        cp.execute("SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,))
        data = cp.fetchone()
        if premium:
            # for 5 times, we get c.fetchone()[1] to c.fetchone()[5] and we add it to the channels list, each time with try except
            for i in range(1, 6):
                # we use the i variable to get the channel id
                try:
                    channels.append(str(data[i]))
                except:
                    pass
    except:
        channels = []

    if api_key is None:
        return  # if the api key is not set, return

    try:
        original_message = await message.channel.fetch_message(
            message.reference.message_id
        )  # check if someone replied to the bot
    except:
        original_message = None  # if not, nobody replied to the bot

    if original_message != None and original_message.author.id != self.bot.user.id:
        original_message = None  # if the message someone replied to is not from the bot, set original_message to None

    # if the message is not in a premium channel and
    # if the message doesn't mention the bot and
    # if the message is not a reply to the bot and
    # if the message is not in the default channel
    # return
    if (
        not str(message.channel.id) in channels
        and message.content.find("<@" + str(self.bot.user.id) + ">") == -1
        and original_message == None
        and str(message.channel.id) != str(channel_id)
    ):
        return

    # if the bot has been used more than max_uses times in the last 24 hours in this guild and the guild is not premium
    # send a message and return
    if (
        uses_count_today >= max_uses
        and premium == 0
        and message.guild.id != 1050769643180146749
    ):
        return await message.channel.send(
            f"The bot has been used more than {str(max_uses)} times in the last 24 hours in this guild. Please try again in 24h."
        )

    # if the bot has been used more than max_uses*5 times in the last 24 hours in this guild and the guild is premium
    # send a message and return
    elif uses_count_today >= max_uses * 5 and premium == 1:
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
    # if the message is not in the owner's guild we update the usage count
    if message.guild.id != 1021872219888033903:
        c.execute(
            "UPDATE data SET uses_count_today = uses_count_today + 1 WHERE guild_id = ?",
            (message.guild.id,),
        )
        conn.commit()
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
    # open the prompt file for the selected model with utf-8 encoding for emojis
    with open(f"./prompts/{model}.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
        f.close()
    # replace the variables in the prompt with the actual values
    prompt = (
        prompt.replace("[prompt-prefix]", prompt_prefix)
        .replace("[server-name]", message.guild.name)
        .replace("[channel-name]", message.channel.name)
        .replace(
            "[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        )
        .replace("[pretend-to-be]", pretend_to_be)
    )
    ############################## chatGPT and gpt-4 handling ##############################
    if (
        model == "chatGPT" or model == "gpt-4"
    ):  # if the model is chatGPT, we handle it in a certain way
        msgs = []  # create the msgs list
        msgs.append(
            {"name": "System", "role": "user", "content": prompt}
        )  # add the prompt to the msgs list
        name = ""  # create the name variable
        for msg in messages:  # for each message in the messages list
            content = msg.content  # get the content of the message
            content = await replace_mentions(
                content, self.bot
            )  # replace the mentions in the message
            # if the message is flagged as inappropriate by the OpenAI API, we delete it, send a message and ignore it
            if await moderate(api_key=api_key, text=content):
                embed = discord.Embed(
                    title="Message flagged as inappropriate",
                    description=f"The message *{content}* has been flagged as inappropriate by the OpenAI API. This means that if it hadn't been deleted, your openai account would have been banned. Please contact OpenAI support if you think this is a mistake.",
                    color=discord.Color.brand_red(),
                )
                await message.channel.send(
                    f"{msg.author.mention}", embed=embed, delete_after=10
                )
                message.delete()
            else:  # if the message is not flagged as inappropriate
                if msg.author.id == self.bot.user.id:
                    role = "assistant"
                    name = "assistant"
                else:
                    role = "user"
                    name = msg.author.name
                    # the name should match '^[a-zA-Z0-9_-]{1,64}$', so we need to remove any special characters
                    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
                if False:  # GPT-4 images
                    input_content = [content]
                    for attachment in msg.attachments:
                        image_bytes = await attachment.read()
                        input_content.append({"image": image_bytes})
                    msgs.append({"role": role, "content": input_content, "name": name})
                # if there is an attachment, we add it to the message
                if len(msg.attachments) > 0 and role == "user" and images_enabled == 1:
                    for attachment in msg.attachments:
                        if images_usage >= 6 and premium == 0:
                            images_limit_reached = True
                        elif images_usage >= 30 and premium == 1:
                            images_limit_reached = True
                        if (
                            attachment.url.endswith((".png", ".jpg", ".jpeg", ".gif"))
                            and images_limit_reached == False
                            and os.path.exists(
                                f"./../database/google-vision/results/{attachment.id}.txt"
                            )
                            == False
                        ):
                            images_usage += 1
                            analysis = await vision_processing.process(attachment)
                            if analysis != None:
                                content = f"{content} \n\n {analysis}"
                                msgs.append(
                                    {
                                        "role": role,
                                        "content": f"{content}",
                                        "name": name,
                                    }
                                )
                        # if the attachment is still an image, we can check if there's a file called ./../database/google-vision/results/{attachment.id}.txt, if there is, we add the content of the file to the message
                        elif (
                            attachment.url.endswith((".png", ".jpg", ".jpeg", ".gif"))
                            and os.path.exists(
                                f"./../database/google-vision/results/{attachment.id}.txt"
                            )
                            == True
                        ):
                            try:
                                with open(
                                    f"./../database/google-vision/results/{attachment.id}.txt",
                                    "r",
                                ) as f:
                                    content = f"{content} \n\n {f.read()}"
                                    f.close()
                                    msgs.append(
                                        {
                                            "role": role,
                                            "content": f"{content}",
                                            "name": name,
                                        }
                                    )
                            except:
                                msgs.append(
                                    {
                                        "role": role,
                                        "content": f"{content}",
                                        "name": name,
                                    }
                                )
                        else:
                            msgs.append(
                                {"role": role, "content": f"{content}", "name": name}
                            )
                    c.execute(
                        "UPDATE images SET usage_count = ? WHERE guild_id = ?",
                        (images_usage, message.guild.id),
                    )
                else:
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
        if model == "chatGPT":
            model = "gpt-3.5-turbo"  # if the model is chatGPT, we set the model to gpt-3.5-turbo
        response = ""
        should_break = True
        for x in range(10):
            try:
                openai.api_key = api_key
                response = await openai.ChatCompletion.acreate(
                    model=model,
                    temperature=2,
                    top_p=0.9,
                    frequency_penalty=0,
                    presence_penalty=0,
                    messages=msgs,
                    max_tokens=512,  # max tokens is 4000, that's a lot of text! (the max tokens is 2048 for the davinci model)
                )
                if (
                    response.choices[0]
                    .message.content.lower()
                    .find("as an ai language model")
                    != -1
                ):
                    should_break = False
                    # react with a redone arrow
                    await message.add_reaction("🔃")
                else:
                    should_break = True
            except Exception as e:
                should_break = False
                await message.channel.send(
                    f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=5
                )
            # if the ai said "as an ai language model..." we continue the loop" (this is a bug in the chatgpt model)
            if response == None:
                should_break = False
            if should_break:
                break
            await asyncio.sleep(15)
            await message.channel.trigger_typing()
        response = response.choices[0].message.content
        if images_limit_reached == True:
            await message.channel.send(
                f"```diff\n-Warning: You have reached the image limit for this server. You can upgrade to premium to get more images recognized. More info in our server: https://discord.gg/sxjHtmqrbf```",
                delete_after=10,
            )
    # -----------------------------------------Davinci------------------------------------------------------------------------------------------

    elif (
        model == "davinci"
    ):  # if the model is davinci or gpt-4, we handle it in a certain way
        for msg in messages:
            content = msg.content
            if await moderate(api_key=api_key, text=msg.content):
                embed = discord.Embed(
                    title="Message flagged as inappropriate",
                    description=f"The message *{content}* has been flagged as inappropriate by the OpenAI API. This means that if it hadn't been deleted, your openai account would have been banned. Please contact OpenAI support if you think this is a mistake.",
                    color=discord.Color.brand_red(),
                )
                await message.channel.send(
                    f"{msg.author.mention}", embed=embed, delete_after=10
                )
                message.delete()
            else:
                content = await replace_mentions(content, self.bot)
                prompt += f"{msg.author.name}: {content}\n"
        if message.content.lower().find("undude") != -1:
            prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
        if message.content.lower().find("hello there") != -1:
            prompt += 'System: Hello there detected. Botator will now say "General Kenobi!"\n in reference to star wars\n'
            await asyncio.sleep(1)
            await message.channel.send(
                "https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif"
            )
            await message.channel.trigger_typing()
        prompt = prompt + f"\n{self.bot.user.name}:"
        response = ""
        for _ in range(10):
            try:
                openai.api_key = api_key
                response = await openai.Completion.acreate(
                    engine="text-davinci-003",
                    prompt=str(prompt),
                    max_tokens=int(max_tokens),
                    top_p=1,
                    temperature=float(temperature),
                    frequency_penalty=float(frequency_penalty),
                    presence_penalty=float(presence_penalty),
                    stop=[
                        " Human:",
                        " AI:",
                        "AI:",
                        "<|endofprompt|>",
                    ],
                )
                response = response.choices[0].text
            except Exception as e:
                response = None
                await message.channel.send(
                    f"```diff\n-Error: OpenAI API ERROR.\n\n{e}```", delete_after=10
                )
                return
            if response != None:
                break
    if response != "":
        if tts:
            tts = True
        else:
            tts = False
        emojis, string = await extract_emoji(response)
        debug(f"Emojis: {emojis}")
        if len(string) < 1996:
            await message.channel.send(string, tts=tts)
        else:
            # we send in an embed if the message is too long
            embed = discord.Embed(
                title="Botator response",
                description=string,
                color=discord.Color.brand_green(),
            )
            await message.channel.send(embed=embed, tts=tts)
        for emoji in emojis:
            # if the emoji is longer than 1 character, it's a custom emoji
            try:
                if len(emoji) > 1:
                    # if the emoji is a custom emoji, we need to fetch it
                    # the emoji is in the format id
                    debug(f"Emoji: {emoji}")
                    emoji = await message.guild.fetch_emoji(int(emoji))
                    await message.add_reaction(emoji)
                else:
                    debug(f"Emoji: {emoji}")
                    await message.add_reaction(emoji)
            except:
                pass
    else:
        await message.channel.send(
            "The AI is not sure what to say (the response was empty)"
        )
