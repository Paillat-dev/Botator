import discord
from src.config import debug, con_data, curs_data, ctx_to_guid
from src.utils.misc import moderate
from discord import default_permissions

models = ["davinci", "gpt-3.5-turbo", "gpt-4"]
images_recognition = ["enable", "disable"]


class Settings(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.slash_command(name="advanced", description="Advanced settings")
    @default_permissions(administrator=True)
    @discord.option(name="max_tokens", description="The max tokens", required=False)
    @discord.option(name="temperature", description="The temperature", required=False)
    @discord.option(
        name="frequency_penalty", description="The frequency penalty", required=False
    )
    @discord.option(
        name="presence_penalty", description="The presence penalty", required=False
    )
    @discord.option(name="prompt_size", description="The prompt size", required=False)
    async def advanced(
        self,
        ctx: discord.ApplicationContext,
        max_tokens: int = None,
        temperature: float = None,
        frequency_penalty: float = None,
        presence_penalty: float = None,
        prompt_size: int = None,
    ):
        await ctx.respond(
            "This command has been deprecated since the new model does not need theese settungs to work well",
            ephemeral=True,
        )

    @discord.slash_command(name="default", description="Default settings")
    @default_permissions(administrator=True)
    async def default(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            "This command has been deprecated since the new model does not need theese settungs to work well",
            ephemeral=True,
        )

    @discord.slash_command(name="prompt_size", description="Set the prompt size")
    @default_permissions(administrator=True)
    @discord.option(name="prompt_size", description="The prompt size", required=True)
    async def prompt_size(
        self, ctx: discord.ApplicationContext, prompt_size: int = None
    ):
        # only command that is not deprecated
        # check if the guild is in the database
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            data = curs_data.fetchone()
        except:
            data = None
        if data[2] is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # check if the prompt size is valid
        if prompt_size is None:
            await ctx.respond("You must specify a prompt size", ephemeral=True)
            return
        if prompt_size < 1 or prompt_size > 15:
            await ctx.respond(
                "The prompt size must be between 1 and 15", ephemeral=True
            )
            return
        # update the prompt size
        curs_data.execute(
            "UPDATE data SET prompt_size = ? WHERE guild_id = ?",
            (prompt_size, ctx_to_guid(ctx)),
        )
        con_data.commit()
        await ctx.respond(f"Prompt size set to {prompt_size}", ephemeral=True)

    # when a message is sent into a channel check if the guild is in the database and if the bot is enabled
    @discord.slash_command(
        name="info", description="Show the information stored about this server"
    )
    @default_permissions(administrator=True)
    async def info(self, ctx: discord.ApplicationContext):
        # this command sends all the data about the guild, including the api key, the channel id, the advanced settings and the uses_count_today
        # check if the guild is in the database
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            data = curs_data.fetchone()
        except:
            data = None
        if data[2] is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        try:
            curs_data.execute(
                "SELECT * FROM model WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            model = curs_data.fetchone()[1]
        except:
            model = None
        if model is None:
            model = "davinci"
        embed = discord.Embed(
            title="Info", description="Here is the info page", color=0x00FF00
        )
        embed.add_field(name="guild_id", value=data[0], inline=False)
        embed.add_field(name="API Key", value="secret", inline=False)
        embed.add_field(name="Main channel ID", value=data[1], inline=False)
        embed.add_field(name="Is Active", value=data[3], inline=False)
        embed.add_field(name="Prompt Size", value=data[9], inline=False)
        if data[10]:
            embed.add_field(name="Prompt prefix", value=data[10], inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="prefix", description="Change the prefix of the prompt")
    @default_permissions(administrator=True)
    async def prefix(self, ctx: discord.ApplicationContext, prefix: str = ""):
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            data = curs_data.fetchone()
            api_key = data[2]
        except:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        if api_key is None or api_key == "":
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        if prefix != "":
            await ctx.defer()
            if await moderate(api_key=api_key, text=prefix):
                await ctx.respond(
                    "This has been flagged as inappropriate by OpenAI, please choose another prefix",
                    ephemeral=True,
                )
                return
        await ctx.respond("Prefix changed !", ephemeral=True, delete_after=5)
        curs_data.execute(
            "UPDATE data SET prompt_prefix = ? WHERE guild_id = ?",
            (prefix, ctx_to_guid(ctx)),
        )
        con_data.commit()

    # when someone mentions the bot, check if the guild is in the database and if the bot is enabled. If it is, send a message answering the mention
    @discord.slash_command(
        name="pretend", description="Make the bot pretend to be someone else"
    )
    @discord.option(
        name="pretend to be...",
        description="The person/thing you want the bot to pretend to be. Leave blank to disable pretend mode",
        required=False,
    )
    @default_permissions(administrator=True)
    async def pretend(self, ctx: discord.ApplicationContext, pretend_to_be: str = ""):
        # check if the guild is in the database
        try:
            curs_data.execute(
                "SELECT * FROM data WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            data = curs_data.fetchone()
            api_key = data[2]
        except:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        if api_key is None or api_key == "":
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        if pretend_to_be is not None or pretend_to_be != "":
            await ctx.defer()
            if await moderate(api_key=api_key, text=pretend_to_be):
                await ctx.respond(
                    "This has been flagged as inappropriate by OpenAI, please choose another name",
                    ephemeral=True,
                )
                return
        if pretend_to_be == "":
            pretend_to_be = ""
            curs_data.execute(
                "UPDATE data SET pretend_enabled = 0 WHERE guild_id = ?",
                (ctx_to_guid(ctx),),
            )
            con_data.commit()
            await ctx.respond("Pretend mode disabled", ephemeral=True, delete_after=5)
            await ctx.guild.me.edit(nick=None)
            return
        else:
            curs_data.execute(
                "UPDATE data SET pretend_enabled = 1 WHERE guild_id = ?",
                (ctx_to_guid(ctx),),
            )
            con_data.commit()
            await ctx.respond("Pretend mode enabled", ephemeral=True, delete_after=5)
            # change the bots name on the server wit ctx.guild.me.edit(nick=pretend_to_be)
            await ctx.guild.me.edit(nick=pretend_to_be)
            curs_data.execute(
                "UPDATE data SET pretend_to_be = ? WHERE guild_id = ?",
                (pretend_to_be, ctx_to_guid(ctx)),
            )
            con_data.commit()
            # if the usename is longer than 32 characters, shorten it
            if len(pretend_to_be) > 31:
                pretend_to_be = pretend_to_be[:32]
            await ctx.guild.me.edit(nick=pretend_to_be)
            return

    @discord.slash_command(name="enable_tts", description="Enable TTS when chatting")
    @default_permissions(administrator=True)
    async def enable_tts(self, ctx: discord.ApplicationContext):
        # get the guild id
        guild_id = ctx_to_guid(ctx)
        # connect to the database
        # update the tts value in the database
        curs_data.execute("UPDATE data SET tts = 1 WHERE guild_id = ?", (guild_id,))
        con_data.commit()
        # send a message
        await ctx.respond("TTS has been enabled", ephemeral=True)

    @discord.slash_command(name="disable_tts", description="Disable TTS when chatting")
    @default_permissions(administrator=True)
    async def disable_tts(self, ctx: discord.ApplicationContext):
        # get the guild id
        guild_id = ctx_to_guid(ctx)
        # connect to the database
        # update the tts value in the database
        curs_data.execute("UPDATE data SET tts = 0 WHERE guild_id = ?", (guild_id,))
        con_data.commit()
        # send a message
        await ctx.respond("TTS has been disabled", ephemeral=True)

    # autocompletition
    async def autocomplete(ctx: discord.AutocompleteContext):
        return [model for model in models if model.startswith(ctx.value)]

    @discord.slash_command(name="model", description="Change the model used by the bot")
    @discord.option(
        name="model",
        description="The model you want to use. Leave blank to use the davinci model",
        required=False,
        autocomplete=autocomplete,
    )
    @default_permissions(administrator=True)
    async def model(self, ctx: discord.ApplicationContext, model: str = "davinci"):
        await ctx.respond(
            "This command has been deprecated. Model gpt-3.5-turbo is always used by default",
            ephemeral=True,
        )

    async def images_recognition_autocomplete(ctx: discord.AutocompleteContext):
        return [state for state in images_recognition if state.startswith(ctx.value)]

    @discord.slash_command(
        name="images", description="Enable or disable images recognition"
    )
    @discord.option(
        name="enable_disable",
        description="Enable or disable images recognition",
        autocomplete=images_recognition_autocomplete,
    )
    @default_permissions(administrator=True)
    async def images(self, ctx: discord.ApplicationContext, enable_disable: str):
        try:
            curs_data.execute(
                "SELECT * FROM images WHERE guild_id = ?", (ctx_to_guid(ctx),)
            )
            data = curs_data.fetchone()
        except:
            data = None
        if enable_disable == "enable":
            enable_disable = 1
        elif enable_disable == "disable":
            enable_disable = 0
        if data is None:
            curs_data.execute(
                "INSERT INTO images VALUES (?, ?, ?)",
                (ctx_to_guid(ctx), 0, enable_disable),
            )
        else:
            curs_data.execute(
                "UPDATE images SET is_enabled = ? WHERE guild_id = ?",
                (enable_disable, ctx_to_guid(ctx)),
            )
        con_data.commit()
        await ctx.respond(
            "Images recognition has been "
            + ("enabled" if enable_disable == 1 else "disabled"),
            ephemeral=True,
        )
