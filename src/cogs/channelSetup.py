import discord
import orjson

from discord import SlashCommandGroup
from discord import default_permissions
from discord.ext.commands import guild_only
from discord.ext import commands
from src.utils.variousclasses import models, characters, apis
from src.guild import Guild

sampleDataFormatExample = {
    "guild_id": 1234567890,
    "premium": False,
    "premium_expiration": 0,
}


class ChannelSetup(commands.Cog):
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot

    setup = SlashCommandGroup(
        "setup",
        description="Setup commands for the bot, inlcuding channels, models, and more.",
    )

    setup_channel = setup.create_subgroup(
        name="channel", description="Setup, add, or remove channels for the bot to use."
    )

    @setup_channel.command(
        name="add",
        description="Add a channel for the bot to use. Can also specify server-wide settings.",
    )
    @discord.option(
        name="channel",
        description="The channel to setup. If not specified, will use the current channel.",
        type=discord.TextChannel,
        required=False,
    )
    @discord.option(
        name="model",
        description="The model to use for this channel.",
        type=str,
        required=False,
        autocomplete=models.autocomplete,
    )
    @discord.option(
        name="character",
        description="The character to use for this channel.",
        type=str,
        required=False,
        autocomplete=characters.autocomplete,
    )
    @guild_only()
    async def channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel = None,
        model: str = models.default,
        character: str = characters.default,
    ):
        if channel is None:
            channel = ctx.channel
        guild = Guild(ctx.guild.id)
        guild.load()
        if not guild.premium:
            if (
                len(guild.channels) >= 1
                and guild.channels.get(str(channel.id), None) is None
            ):
                await ctx.respond(
                    "`Warning: You are not a premium user, and can only have one channel setup. The settings will still be saved, but will not be used.`",
                    ephemeral=True,
                )
            if model != models.default:
                await ctx.respond(
                    "`Warning: You are not a premium user, and can only use the default model. The settings will still be saved, but will not be used.`",
                    ephemeral=True,
                )
            if character != characters.default:
                await ctx.respond(
                    "`Warning: You are not a premium user, and can only use the default character. The settings will still be saved, but will not be used.`",
                    ephemeral=True,
                )
        if guild.api_keys.get("openai", None) is None:
            await ctx.respond(
                "`Error: No openai api key is set. The api key is needed for the openai models, as well as for the content moderation. The openai models will cost you tokens in your openai account. However, if you use one of the llama models, you will not be charged, but the api key is still needed for content moderation, wich is free but requires an api key.`",
                ephemeral=True,
            )
        guild.addChannel(
            channel, models.matchingDict[model], characters.matchingDict[character]
        )
        await ctx.respond(
            f"Set channel {channel.mention} with model `{model}` and character `{character}`."
        )

    @setup_channel.command(
        name="remove", description="Remove a channel from the bot's usage."
    )
    @discord.option(
        name="channel",
        description="The channel to remove. If not specified, will use the current channel.",
        type=discord.TextChannel,
        required=False,
    )
    @guild_only()
    async def remove(
        self, ctx: discord.ApplicationContext, channel: discord.TextChannel = None
    ):
        if channel is None:
            channel = ctx.channel
        guild = Guild(ctx.guild.id)
        guild.load()
        if channel.id not in guild.channels:
            await ctx.respond("That channel is not setup.")
            return
        guild.delChannel(channel)
        await ctx.respond(f"Removed channel {channel.mention}.")

    @setup_channel.command(name="list", description="List all channels that are setup.")
    @guild_only()
    async def list(self, ctx: discord.ApplicationContext):
        guild = Guild(ctx.guild.id)
        guild.load()
        if len(guild.channels) == 0:
            await ctx.respond("No channels are setup.")
            return
        embed = discord.Embed(
            title="Channels",
            description="All channels that are setup.",
            color=discord.Color.nitro_pink(),
        )
        channels = guild.sanitizedChannels
        for channel in channels:
            discochannel = await self.bot.fetch_channel(int(channel))
            model = models.reverseMatchingDict[channels[channel]["model"]]
            character = characters.reverseMatchingDict[channels[channel]["character"]]
            embed.add_field(
                name=f"{discochannel.mention}",
                value=f"Model: `{model}`\nCharacter: `{character}`",
                inline=False,
            )
        await ctx.respond(embed=embed)

    @setup.command(name="api", description="Set an API key for the bot to use.")
    @discord.option(
        name="api",
        description="The API to set. Currently only OpenAI is supported.",
        type=str,
        required=True,
        autocomplete=apis.autocomplete,
    )
    @discord.option(name="key", description="The key to set.", type=str, required=True)
    @guild_only()
    async def api(self, ctx: discord.ApplicationContext, api: str, key: str):
        guild = Guild(ctx.guild.id)
        guild.load()
        guild.api_keys[apis.matchingDict[api]] = key
        guild.updateDbData()
        await ctx.respond(f"Set API key for {api} to `secret`.", ephemeral=True)

    @setup.command(name="premium", description="Set the guild to premium.")
    async def premium(self, ctx: discord.ApplicationContext):
        guild = Guild(ctx.guild.id)
        guild.load()
        if not guild.premium:
            await ctx.respond(
                "You can get your premium subscription at https://www.botator.dev/premium.",
                ephemeral=True,
            )
        else:
            await ctx.respond("This guild is already premium.", ephemeral=True)
