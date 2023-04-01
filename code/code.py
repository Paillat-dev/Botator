import discord 
from discord import Intents
import cogs # import the cogs
from config import debug, discord_token
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents, help_command=None)
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




@bot.event
async def on_application_command_error(ctx, error):
    debug(error)
    await ctx.respond(error, ephemeral=True)
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="your messages to answer you"
        )
    )
    debug("Bot is ready")

bot.run(discord_token)