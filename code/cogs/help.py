import discord
from config import debug

class Help (discord.Cog) :
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.slash_command(name="help", description="Show all the commands")
    async def help(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author} ran the help command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        embed = discord.Embed(title="Help", description="Here is the help page", color=0x00ff00)
        embed.add_field(name="/setup", value="Setup the bot", inline=False)
        embed.add_field(name="/enable", value="Enable the bot", inline=False)
        embed.add_field(name="/disable", value="Disable the bot", inline=False)
        embed.add_field(name="/advanced", value="Set the advanced settings", inline=False)
        embed.add_field(name="/advanced_help", value="Get help about the advanced settings", inline=False)
        embed.add_field(name="/enable_tts", value="Enable the Text To Speech", inline=False)
        embed.add_field(name="/disable_tts", value="Disable the Text To Speech", inline=False)
        embed.add_field(name="/add|remove_channel", value="Add or remove a channel to the list of channels where the bot will answer. Only available on premium guilds", inline=False)
        embed.add_field(name="/delete", value="Delete all your data from our server", inline=False)
        embed.add_field(name="/cancel", value="Cancel the last message sent by the bot", inline=False)
        embed.add_field(name="/default", value="Set the advanced settings to their default values", inline=False)
        embed.add_field(name="/help", value="Show this message", inline=False)
        #add a footer
        embed.set_footer(text="Made by @Paillat#7777, made less annoying by rhiza#0001")
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="advanced_help", description="Show the advanced settings meanings")
    async def advanced_help(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author} ran the advanced_help command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        embed = discord.Embed(title="Advanced Help", description="Here is the advanced help page", color=0x00ff00)
        embed.add_field(name="temperature", value="The higher the temperature, the more likely the model will take risks. Conversely, a lower temperature will make the model more conservative. The default value is 0.9", inline=False)
        embed.add_field(name="max_tokens", value="The maximum number of tokens to generate. Higher values will result in more coherent text, but will take longer to complete. (default: 50). **Lower values will result in somentimes cutting off the end of the answer, but will be faster.**", inline=False)
        embed.add_field(name="frequency_penalty", value="The higher the frequency penalty, the more new words the model will introduce (default: 0.0)", inline=False)
        embed.add_field(name="presence_penalty", value="The higher the presence penalty, the more new words the model will introduce (default: 0.0)", inline=False)
        embed.add_field(name="prompt_size", value="The number of messages to use as a prompt (default: 5). The more messages, the more coherent the text will be, but the more it will take to generate and the more it will cost.", inline=False)
        #add a footer
        embed.set_footer(text="Made by @Paillat#7777, made less annoying by rhiza#0001")
        await ctx.respond(embed=embed, ephemeral=True)
