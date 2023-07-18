import discord
import aiohttp

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

unsplash_random_image_url = "https://source.unsplash.com/random"


async def get_final_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url, allow_redirects=True) as response:
            final_url = str(response.url)
            return final_url


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
