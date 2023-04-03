import asyncio
from config import curs_data, max_uses, curs_premium, con_data, debug, moderate
import vision_processing
import re
import discord
import datetime
import openai
import emoji
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
        # if the match is an emoji, we replace it with the match
        if emoji.emoji_count(match) > 0:
            found_emojis.append(match)
            string = string.replace(
                f"+{match}", ""
            )  # we remove the emoji from the string
    for match in custom_emoji_matches:
        found_emojis.append(match[1])
        string = string.replace(f"+<:{match[0]}:{match[1]}>", "")
    return found_emojis, string


def get_guild_data(message):
    """This function gets the data of the guild where the message was sent.

    Args:
        message (str): Data of the message that was sent

    Returns:
        dict: A dictionary with the data of the guild
    """
    guild_data = {}
    try:
        curs_premium.execute(
            "SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
    except:
        pass

    try:
        curs_data.execute(
            "SELECT * FROM model WHERE guild_id = ?", (message.guild.id,)
        )  # get the model in the database
        data = curs_data.fetchone()
        model = data[1]
    except:
        model = "gpt-3.5-turbo"

    try:
        # [2]  # get the premium status of the guild
        data = curs_premium.fetchone()
        premium = data[2]
    except:
        premium = 0  # if the guild is not in the database, it's not premium

    try:
        curs_data.execute(
            "SELECT * FROM images WHERE guild_id = ?", (message.guild.id,)
        )  # get the images setting in the database
        images = curs_data.fetchone()
    except:
        images = None

    guild_data["model"] = "gpt-3.5-turbo" if model == "chatGPT" else model
    debug(f"Model: {guild_data['model']}")
    debug(f"Model from database: {model}")
    guild_data["premium"] = premium
    guild_data["images"] = images
    
    guild_data["images_limit_reached"] = False

    return guild_data


async def need_ignore_message(bot, data_dict, message, guild_data, original_message, channels):
    ## ---- Message ignore conditions ---- ##
    if data_dict["api_key"] is None:
        return True  # if the api key is not set, return

    if (
        # if the message is not in a premium channel and
        not (str(message.channel.id) in channels
             # if the message doesn't mention the bot and
             and (message.content.find("<@" + str(bot.user.id) + ">") != -1
                  or original_message))  # if the message is not a reply to the bot and
        # if the message is not in the default channel
        and str(message.channel.id) != str(data_dict["channel_id"])
    ):
        return True

    # if the bot has been used more than max_uses*5 times in the last 24 hours in this guild and the guild is premium
    # send a message and return
    elif data_dict["uses_count_today"] >= max_uses * 5 and guild_data["premium"] == 1:
        return True

    # if the bot is not active in this guild we return
    if data_dict["is_active"] == 0:
        return True

    # if the message starts with - or // it's a comment and we return
    if message.content.startswith("-") or message.content.startswith("//"):
        return True

    # if the bot has been used more than max_uses times in the last 24 hours in this guild and the guild is not premium
    # send a message and return
    if (
        data_dict["uses_count_today"] >= max_uses
        and guild_data["premium"] == 0
        and message.guild.id != 1050769643180146749
    ):
        await message.channel.send(
            f"The bot has been used more than {str(max_uses)} times in the last 24 hours in this guild. Please try again in 24h."
        )
        return True
    return False


async def get_data_dict(message):
    try:
        curs_data.execute(
            "SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
        data = curs_data.fetchone()
        # Create a dict with the data
        data_dict = {
            "channel_id": data[1],
            "api_key": data[2],
            "is_active": data[3],
            "max_tokens": data[4],
            "temperature": data[5],
            "frequency_penalty": data[6],
            "presence_penalty": data[7],
            "uses_count_today": data[8],
            "prompt_size": data[9],
            "prompt_prefix": data[10],
            "tts": bool(data[11]),
            "pretend_to_be": data[12],
            "pretend_enabled": data[13],
        }
        return data_dict
    except Exception as e:
        # Send an error message
        await message.channel.send(
            "The bot is not configured yet. Please use `//setup` to configure it. \n" +
            "If it still doesn't work, it might be a database error. \n ```" + e.__str__()
            + "```", delete_after=60
        )

def get_prompt(guild_data, data_dict, message, pretend_to_be):
    # support for custom prompts
    custom_prompt_path = f"../database/prompts/{guild_data['model']}.txt"
    if(os.path.exists(custom_prompt_path)):
        prompt_path = custom_prompt_path
    else:
        prompt_path = f"./prompts/{guild_data['model']}.txt"
    
    # open the prompt file for the selected model with utf-8 encoding for emojis
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
        # replace the variables in the prompt with the actual values
        prompt = (
            prompt.replace("[prompt-prefix]", data_dict['prompt_prefix'])
            .replace("[server-name]", message.guild.name)
            .replace("[channel-name]", message.channel.name)
            .replace(
                "[date-and-time]", datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
            )
            .replace("[pretend-to-be]", pretend_to_be)
        )
        f.close()
    return prompt

async def chat_process(self, message):
    """This function processes the message and sends the prompt to the API

    Args:
        message (str): Data of the message that was sent
    """
    if message.author.bot:
        return

    guild_data = get_guild_data(message)
    data_dict = await get_data_dict(message)

    try:
        original_message = await message.channel.fetch_message(
            message.reference.message_id
        )  # check if someone replied to the bot
    except:
        original_message = None  # if not, nobody replied to the bot

    if original_message != None and original_message.author.id != self.bot.user.id:
        # if the message someone replied to is not from the bot, set original_message to None
        original_message = None

    try:
        # get the images setting in the database
        curs_data.execute(
            "SELECT * FROM images WHERE guild_id = ?", (message.guild.id,))
        images_data = curs_data.fetchone()
    except:
        images_data = None

    ## ---- Message processing ---- ##

    if not images_data:
        images_data = [message.guild.id, 0, 0]

    data_dict["images_usage"] = 0 if message.guild.id == 1050769643180146749 else images_data[1]
    data_dict["images_enabled"] = images_data[2]


    channels = []
    try:
        curs_premium.execute(
            "SELECT * FROM channels WHERE guild_id = ?", (message.guild.id,))
        images_data = curs_premium.fetchone()
        if guild_data["premium"]:
            # for 5 times, we get c.fetchone()[1] to c.fetchone()[5] and we add it to the channels list, each time with try except
            for i in range(1, 6):
                # we use the i variable to get the channel id
                try:
                    channels.append(str(images_data[i]))
                except:
                    pass
    except:
        debug("No premium channels found for this guild")

    if (await need_ignore_message(self.bot, data_dict, message, guild_data, original_message, channels)):
        return

    try:
        await message.channel.trigger_typing()
        # if the message is not in the owner's guild we update the usage count
        if message.guild.id != 1021872219888033903:
            curs_data.execute(
                "UPDATE data SET uses_count_today = uses_count_today + 1 WHERE guild_id = ?",
                (message.guild.id,),
            )
            con_data.commit()
        # if the message is not a reply
        if original_message == None:
            messages = await message.channel.history(
                limit=data_dict["prompt_size"]
            ).flatten()
            messages.reverse()
        # if the message is a reply, we need to handle the message history differently
        else:
            messages = await message.channel.history(
                limit=data_dict["prompt_size"], before=original_message
            ).flatten()
            messages.reverse()
            messages.append(original_message)
            messages.append(message)
    except Exception as e:
        debug("Error while getting message history", e)

    # if the pretend to be feature is enabled, we add the pretend to be text to the prompt
    pretend_to_be = data_dict["pretend_to_be"]
    pretend_to_be = f"In this conversation, the assistant pretends to be {pretend_to_be}" if data_dict[ "pretend_enabled"] else ""
    debug(f"Pretend to be: {pretend_to_be}")
    prompt = get_prompt(guild_data, data_dict, message, pretend_to_be)

    prompt_handlers = {
        "gpt-3.5-turbo": gpt_prompt,
        "gpt-4": gpt_prompt,
        "davinci": davinci_prompt,
    }
    debug(guild_data["model"])
    response = await prompt_handlers[guild_data["model"]](
        self.bot, messages, message, data_dict, prompt, guild_data
    )
    
    if response != "":
        emojis, string = await extract_emoji(response)
        debug(f"Emojis: {emojis}")
        if len(string) < 1996:
            await message.channel.send(string, tts=data_dict["tts"])
        else:
            # we send in an embed if the message is too long
            embed = discord.Embed(
                title="Botator response",
                description=string,
                color=discord.Color.brand_green(),
            )
            await message.channel.send(embed=embed, tts=data_dict["tts"])
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


async def check_moderate(api_key, message, msg):
    if await moderate(api_key=api_key, text=msg.content):
        embed = discord.Embed(
            title="Message flagged as inappropriate",
            description=f"The message *{msg.content}* has been flagged as inappropriate by the OpenAI API. This means that if it hadn't been deleted, your openai account would have been banned. Please contact OpenAI support if you think this is a mistake.",
            color=discord.Color.brand_red(),
        )
        await message.channel.send(
            f"{msg.author.mention}", embed=embed, delete_after=10
        )
        message.delete()
        return True
    return False


async def check_easter_egg(message, msgs):
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
    return msgs


async def gpt_prompt(bot, messages, message, data_dict, prompt, guild_data):
    debug("Using GPT-3.5 Turbo prompt")
    msgs = []  # create the msgs list
    msgs.append(
        {"name": "System", "role": "user", "content": prompt}
    )  # add the prompt to the msgs list
    name = ""  # create the name variable
    for msg in messages:  # for each message in the messages list
        content = msg.content  # get the content of the message
        content = await replace_mentions(
            content, bot
        )  # replace the mentions in the message
        # if the message is flagged as inappropriate by the OpenAI API, we delete it, send a message and ignore it
        if await check_moderate(data_dict["api_key"], message, msg):
            continue  # ignore the message
        content = await replace_mentions(content, bot)
        prompt += f"{msg.author.name}: {content}\n"
        if msg.author.id == bot.user.id:
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
        if (
            len(msg.attachments) > 0
            and role == "user"
            and data_dict["images_enabled"] == 1
        ):
            for attachment in msg.attachments:
                path = f"./../database/google-vision/results/{attachment.id}.txt"
                if data_dict['images_usage'] >= 6 and guild_data["premium"] == 0:
                    guild_data["images_limit_reached"] = True
                elif data_dict['images_usage'] >= 30 and guild_data["premium"] == 1:
                    guild_data["images_limit_reached"] = True
                if (
                    attachment.url.endswith((".png", ".jpg", ".jpeg", ".gif"))
                    and not guild_data["images_limit_reached"]
                    and not os.path.exists(path)
                ):
                    data_dict['images_usage'] += 1
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
                elif attachment.url.endswith(
                    (".png", ".jpg", ".jpeg", ".gif")
                ) and os.path.exists(path):
                    try:
                        with open(
                            path,
                            "r",
                        ) as f:
                            content = f"{content} \n\n {f.read()}"
                    except:
                        debug(f"Error while reading {path}")
                    finally:
                        msgs.append(
                            {
                                "role": role,
                                "content": f"{content}",
                                "name": name,
                            }
                        )
                        f.close()

                else:
                    msgs.append(
                        {"role": role, "content": f"{content}", "name": name}
                    )
            curs_data.execute(
                "UPDATE images SET usage_count = ? WHERE guild_id = ?",
                (data_dict['images_usage'], message.guild.id),
            )
        else:
            msgs.append({"role": role, "content": f"{content}", "name": name})

    # We check for the eastereggs :)
    msgs = await check_easter_egg(message, msgs)

    response = ""
    should_break = True
    for x in range(10):
        try:
            openai.api_key = data_dict["api_key"]
            response = await openai.ChatCompletion.acreate(
                model=guild_data["model"],
                temperature=2,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0,
                messages=msgs,
                # max tokens is 4000, that's a lot of text! (the max tokens is 2048 for the davinci model)
                max_tokens=512,
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
    
    if guild_data["images_limit_reached"]:
        await message.channel.send(
            f"```diff\n-Warning: You have reached the image limit for this server. You can upgrade to premium to get more images recognized. More info in our server: https://discord.gg/sxjHtmqrbf```",
            delete_after=10,
        )
    return response


async def davinci_prompt(self, messages, message, data_dict, prompt, guild_data):
    debug("davinci_prompt")
    for msg in messages:
        if not await self.check_moderate(data_dict["api_key"], message, msg):
            content = await replace_mentions(content, self.bot)
            prompt += f"{msg.author.name}: {content}\n"
        prompt.append(await check_easter_egg(message, prompt))
    prompt = prompt + f"\n{self.bot.user.name}:"
    response = ""
    for _ in range(10):
        try:
            openai.api_key = data_dict["api_key"]
            response = await openai.Completion.acreate(
                engine="text-davinci-003",
                prompt=str(prompt),
                max_tokens=int(data_dict["max_tokens"]),
                top_p=1,
                temperature=float(data_dict["temperature"]),
                frequency_penalty=float(data_dict["frequency_penalty"]),
                presence_penalty=float(data_dict["presence_penalty"]),
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
        return response