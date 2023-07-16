import discord  # discord.py
from discord import Intents
import src.cogs as cogs
from src.config import debug, discord_token

# add the message content intent to the bot, aka discord.Intents.default() and discord.Intents.message_content
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents, help_command=None)  # create the bot
bot.add_cog(cogs.Setup(bot))
bot.add_cog(cogs.Settings(bot))
bot.add_cog(cogs.Help(bot))
bot.add_cog(cogs.Chat(bot))
bot.add_cog(cogs.ManageChat(bot))
bot.add_cog(cogs.Moderation(bot))


# set the bot's watching status to watcing your messages to answer you
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="your messages to answer you"
        )
    )
    debug("Bot is ready")


@bot.event
async def on_application_command_error(ctx, error):
    debug(error)
    await ctx.respond(error, ephemeral=True)


bot.run(discord_token)  # run the bot