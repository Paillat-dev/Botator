#coucou c'est fives
# wesh wesh ici latouff
import discord # pip install pycord
from discord import Intents
import asyncio # pip install asyncio
import cogs # import the cogs
import datetime # pip install datetime
from config import debug, conn, c, discord_token
#add the message content intent to the bot, aka discord.Intents.default() and discord.Intents.message_content
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents, help_command=None) # create the bot
bot.add_cog(cogs.Setup(bot))
bot.add_cog(cogs.Settings(bot))
bot.add_cog(cogs.Help(bot))
bot.add_cog(cogs.Chat(bot))
bot.add_cog(cogs.ManageChat(bot))
bot.add_cog(cogs.Moderation(bot))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your messages to answer you"))
    debug("Bot is ready")


bot.run(discord_token) # run the bot
#set the bot's watching status to watcing your messages to answer you
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your messages to answer you"))
    debug("Bot is ready")
