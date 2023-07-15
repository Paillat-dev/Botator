import discord

unsplash_random_image_url = "https://source.unsplash.com/random/1920x1080"
async def add_reaction_to_last_message(message_to_react_to: discord.Message, emoji, message=""):
    if message == "":
        await message_to_react_to.add_reaction(emoji)
    else:
        await message_to_react_to.channel.send(message)
        await message_to_react_to.add_reaction(emoji)

async def reply_to_last_message(message_to_reply_to: discord.Message, message):
    await message_to_reply_to.reply(message)

async def send_a_stock_image(message_in_channel_in_wich_to_send: discord.Message, query: str, message:str = ""):
    query = query.replace(" ", "+")
    if message == "":
        await message_in_channel_in_wich_to_send.channel.send(f"https://source.unsplash.com/random/1920x1080?{query}")
    else:
        await message_in_channel_in_wich_to_send.channel.send(message)
        await message_in_channel_in_wich_to_send.channel.send(f"https://source.unsplash.com/random/1920x1080?{query}")