import discord
import asyncio
import aiohttp
import random
import time
from bs4 import BeautifulSoup
from src.config import tenor_api_key

randomseed = time.time()
random.seed(randomseed)
tenor_api_url = f"https://tenor.googleapis.com/v2/search?key={tenor_api_key}&q="

functions = [
    {
        "name": "add_reaction_to_last_message",
        "description": "React to the last message sent by the user with an emoji.",
        "parameters": {
            "type": "object",
            "properties": {
                "emoji": {
                    "type": "string",
                    "description": "an emoji to react with, only one emoji is supported",
                },
                "message": {"type": "string", "description": "Your message"},
            },
            "required": ["emoji"],
        },
    },
    {
        "name": "reply_to_last_message",
        "description": "Reply to the last message sent by the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Your message"}
            },
            "required": ["message"],
        },
    },
    {
        "name": "send_a_stock_image",
        "description": "Send a stock image in the channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for, words separated by spaces",
                },
                "message": {
                    "type": "string",
                    "description": "Your message to send with the image",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "send_a_gif",
        "description": "Send a gif in the channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for, words separated by spaces",
                },
                "message": {
                    "type": "string",
                    "description": "Your message to send with the gif",
                },
                "limit": {
                    "type": "integer",
                    "description": "The number of gifs to search for, a random one will be chosen. If the gif is a really specific one, you might want to have a lower limit, to avoid sending a gif that doesn't match your query.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "send_ascii_art_text",
        "description": "Sendsa message in huge ascii art text.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to send as ascii art",
                },
                "font": {
                    "type": "string",
                    "description": "The font to use, between 'standard'(default), 'shadow', 'money' (made out of $), 'bloody', 'dos-rebel'(like in the matrix, a really cool one). Remember to use this with not too long text (max 5 characters), otherwise it will look weird. To send multiple max 5 length word, add line breaks between them.",
                },
                "message": {
                    "type": "string",
                    "description": "Your message to send with the ascii art. It will not be converted to ascii art, just sent as a normal message.",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "send_ascii_art_image",
        "description": "Sends an image in ascii art.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for, words separated by spaces, max 2 words",
                },
                "message": {
                    "type": "string",
                    "description": "Your message to send with the image",
                },
            },
            "required": ["query"],
        },
    },
]

server_normal_channel_functions = [
    {
        "name": "create_a_thread",
        "description": "Create a thread in the channel. Use this if you see a long discussion coming.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the thread"},
                "message": {
                    "type": "string",
                    "description": "Your message to send with the thread",
                },
            },
            "required": ["name", "message"],
        },
    },
]

font_matches = {
    "standard": "ANSI Regular",
    "shadow": "ANSI Shadow",
    "money": random.choice(
        ["Big Money-ne", "Big Money-nw", "Big Money-se", "Big Money-sw"]
    ),
    "bloody": "Bloody",
    "dos-rebel": "DOS Rebel",
}

unsplash_random_image_url = "https://source.unsplash.com/random"


async def get_final_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url, allow_redirects=True) as response:
            final_url = str(response.url)
            return final_url


async def do_async_request(url, json=True):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if json:
                response = await response.json()
            else:
                response = await response.text()
            return response


async def add_reaction_to_last_message(
    message_to_react_to: discord.Message, emoji, message=""
):
    if message == "":
        await message_to_react_to.add_reaction(emoji)
    else:
        await message_to_react_to.channel.send(message)
        await message_to_react_to.add_reaction(emoji)


async def reply_to_last_message(message_to_reply_to: discord.Message, message):
    await message_to_reply_to.reply(message)


async def send_a_stock_image(
    message_in_channel_in_wich_to_send: discord.Message, query: str, message: str = ""
):
    query = query.replace(" ", "+")
    image_url = f"{unsplash_random_image_url}?{query}"
    final_url = await get_final_url(image_url)
    message = message + "\n" + final_url
    await message_in_channel_in_wich_to_send.channel.send(message)


async def create_a_thread(
    channel_in_which_to_create_the_thread: discord.TextChannel, name: str, message: str
):
    msg = await channel_in_which_to_create_the_thread.send(message)
    await msg.create_thread(name=name)


async def send_a_gif(
    message_in_channel_in_wich_to_send: discord.Message,
    query: str,
    message: str = "",
    limit: int = 15,
):
    query = query.replace(" ", "+")
    image_url = f"{tenor_api_url}{query}&limit={limit}"
    response = await do_async_request(image_url)
    json = response
    gif_url = random.choice(json["results"])["itemurl"]  # type: ignore
    message = message + "\n" + gif_url
    await message_in_channel_in_wich_to_send.channel.send(message)


async def send_ascii_art_text(
    message_in_channel_in_wich_to_send: discord.Message,
    text: str,
    font: str = "standard",
    message: str = "",
):
    font = font_matches[font]
    text = text.replace(" ", "+")
    asciiiar_url = (
        f"https://asciified.thelicato.io/api/v2/ascii?text={text}&font={font}"
    )
    print(asciiiar_url)
    ascii_art = await do_async_request(asciiiar_url, json=False)
    final_message = f"```\n{ascii_art}```\n{message}"
    if len(final_message) < 2000:
        await message_in_channel_in_wich_to_send.channel.send(final_message)
    else:
        if len(ascii_art) < 2000:
            await message_in_channel_in_wich_to_send.channel.send(ascii_art)
        elif len(ascii_art) < 8000:
            embed = discord.Embed(
                title="Ascii art",
                description=ascii_art,)
            await message_in_channel_in_wich_to_send.channel.send(embed=embed)
        else:
            await message_in_channel_in_wich_to_send.channel.send(
                "Sorry, the ascii art is too big to be sent"
            )
        if len(message) < 2000:
            await message_in_channel_in_wich_to_send.channel.send(message
            )
        else:
            while len(message) > 0:
                await message_in_channel_in_wich_to_send.channel.send(message[:2000])
                message = message[2000:]


async def send_ascii_art_image(
    message_in_channel_in_wich_to_send: discord.Message, query: str, message: str = ""
):
    query = query.replace(" ", "-")
    asciiiar_url = f"https://emojicombos.com/{query}"
    response = await do_async_request(asciiiar_url, json=False)
    soup = BeautifulSoup(response, "html.parser")
    combos = soup.find_all("div", class_=lambda x: x and "combo-ctn" in x and "hidden" not in x)[:5]  # type: ignore
    combos = [
        combo["data-combo"] for combo in combos if len(combo["data-combo"]) <= 2000
    ]
    combo = random.choice(combos)
    message = f"```\n{combo}```\n{message}"
    await message_in_channel_in_wich_to_send.channel.send(message)
