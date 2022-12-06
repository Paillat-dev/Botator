import discord
from discord.ext import commands
from discord import File, Intents # pip install pycord

class Disableenable(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot # bot is the client


    @commands.command()