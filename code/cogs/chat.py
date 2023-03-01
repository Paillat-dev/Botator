import discord
import re
import asyncio
import openai
from config import debug, c, max_uses, cp, conn, connp
import random
import threading
import makeprompt as mp
class Chat (discord.Cog) :
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        try: 
            c.execute("SELECT * FROM model WHERE guild_id = ?", (message.guild.id,))
            model = c.fetchone()[1]
        except: model = "davinci"
        if model == "davinci":
            await mp.davinci_process(self, message)
        if model == "chatGPT":
            await mp.chat_process(self, message)

    @discord.slash_command(name="say", description="Say a message")
    async def say(self, ctx: discord.ApplicationContext, message: str):
        await ctx.respond("Message sent !", ephemeral=True)
        await ctx.send(message)

    @discord.slash_command(name="redo", description="Redo a message")
    async def redo(self, ctx: discord.ApplicationContext):
        history = await ctx.channel.history(limit=2).flatten()
        message_to_delete = history[0]
        message_to_redo = history[1]
        if message_to_delete.author.id == self.bot.user.id:
            await message_to_delete.delete()
        else:
            await ctx.respond("The last message wasn't sent by the bot", ephemeral=True)
            return
        #get the message before the  last message, because the new last message is the bot thinking message, so the message before the last message is the message to redo
            await ctx.respond("The message to redo was sent by the bot", ephemeral=True)
            return
        await ctx.respond("Message redone !", ephemeral=True)
        await mp.process(self, message_to_redo)