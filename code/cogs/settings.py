import discord
from config import debug, con_data, curs_data, moderate
from discord import default_permissions
import openai

models = ["davinci", "chatGPT", "gpt-4"]
images_recognition = ["enable", "disable"]


class Settings(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    # create a command called "advanced" that only admins can use, wich sets the advanced settings up: max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size
    @discord.slash_command(name="advanced", description="Advanced settings")
    ##@discord.commands.permissions(administrator=True)
    # add the options
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
        debug(
            f"The user {ctx.author} ran the advanced command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # check if the user has entered at least one argument
        if (
            max_tokens is None
            and temperature is None
            and frequency_penalty is None
            and presence_penalty is None
            and prompt_size is None
        ):
            await ctx.respond("You must enter at least one argument", ephemeral=True)
            return
        # check if the user has entered valid arguments
        if max_tokens is not None and (max_tokens < 1 or max_tokens > 4000):
            await ctx.respond("Invalid max tokens", ephemeral=True)
            return
        if temperature is not None and (temperature < 0.0 or temperature > 1.0):
            await ctx.respond("Invalid temperature", ephemeral=True)
            return
        if frequency_penalty is not None and (
            frequency_penalty < 0.0 or frequency_penalty > 2.0
        ):
            await ctx.respond("Invalid frequency penalty", ephemeral=True)
            return
        if presence_penalty is not None and (
            presence_penalty < 0.0 or presence_penalty > 2.0
        ):
            await ctx.respond("Invalid presence penalty", ephemeral=True)
            return
        if prompt_size is not None and (prompt_size < 1 or prompt_size > 10):
            await ctx.respond("Invalid prompt size", ephemeral=True)
            return
        if max_tokens is None:
            if (
                curs_data.execute(
                    "SELECT max_tokens FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
                is not None
                and max_tokens is None
            ):
                max_tokens = curs_data.execute(
                    "SELECT max_tokens FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
            else:
                max_tokens = 64
        if temperature is None:
            if (
                curs_data.execute(
                    "SELECT temperature FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
                is not None
                and temperature is None
            ):
                temperature = curs_data.execute(
                    "SELECT temperature FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
            else:
                temperature = 0.9
        if frequency_penalty is None:
            if (
                curs_data.execute(
                    "SELECT frequency_penalty FROM data WHERE guild_id = ?",
                    (ctx.guild.id,),
                ).fetchone()[0]
                is not None
                and frequency_penalty is None
            ):
                frequency_penalty = curs_data.execute(
                    "SELECT frequency_penalty FROM data WHERE guild_id = ?",
                    (ctx.guild.id,),
                ).fetchone()[0]
            else:
                frequency_penalty = 0.0
        if presence_penalty is None:
            if (
                curs_data.execute(
                    "SELECT presence_penalty FROM data WHERE guild_id = ?",
                    (ctx.guild.id,),
                ).fetchone()[0]
                is not None
                and presence_penalty is None
            ):
                presence_penalty = curs_data.execute(
                    "SELECT presence_penalty FROM data WHERE guild_id = ?",
                    (ctx.guild.id,),
                ).fetchone()[0]
            else:
                presence_penalty = 0.0
        if prompt_size is None:
            if (
                curs_data.execute(
                    "SELECT prompt_size FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
                is not None
                and prompt_size is None
            ):
                prompt_size = curs_data.execute(
                    "SELECT prompt_size FROM data WHERE guild_id = ?", (ctx.guild.id,)
                ).fetchone()[0]
            else:
                prompt_size = 1
        # update the database
        curs_data.execute(
            "UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?",
            (
                max_tokens,
                temperature,
                frequency_penalty,
                presence_penalty,
                prompt_size,
                ctx.guild.id,
            ),
        )
        con_data.commit()
        await ctx.respond("Advanced settings updated", ephemeral=True)
        # create a command called "delete" that only admins can use wich deletes the guild id, the api key, the channel id and the advanced settings from the database

    @discord.slash_command(name="default", description="Default settings")
    ##@discord.commands.permissions(administrator=True)
    async def default(self, ctx: discord.ApplicationContext):
        debug(
            f"The user {ctx.author} ran the default command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond(
                "This server is not setup, please run /setup", ephemeral=True
            )
            return
        # set the advanced settings (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size) and also prompt_prefix to their default values
        curs_data.execute(
            "UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?",
            (64, 0.9, 0.0, 0.0, 5, ctx.guild.id),
        )
        con_data.commit()
        await ctx.respond(
            "The advanced settings have been set to their default values",
            ephemeral=True,
        )

    # create a command called "cancel" that deletes the last message sent by the bot in the response channel

    # when a message is sent into a channel check if the guild is in the database and if the bot is enabled
    @discord.slash_command(
        name="info", description="Show the information stored about this server"
    )
    async def info(self, ctx: discord.ApplicationContext):
        debug(
            f"The user {ctx.author} ran the info command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # this command sends all the data about the guild, including the api key, the channel id, the advanced settings and the uses_count_today
        # check if the guild is in the database
        try:
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
            data = curs_data.fetchone()
        except:
            data = None
        if data[2] is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        try:
            curs_data.execute("SELECT * FROM model WHERE guild_id = ?", (ctx.guild.id,))
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
        embed.add_field(name="Model", value=model, inline=False)
        embed.add_field(name="Is Active", value=data[3], inline=False)
        embed.add_field(name="Max Tokens", value=data[4], inline=False)
        embed.add_field(name="Temperature", value=data[5], inline=False)
        embed.add_field(name="Frequency Penalty", value=data[6], inline=False)
        embed.add_field(name="Presence Penalty", value=data[7], inline=False)
        embed.add_field(name="Prompt Size", value=data[9], inline=False)
        embed.add_field(name="Uses Count Today", value=data[8], inline=False)
        if data[10]:
            embed.add_field(name="Prompt prefix", value=data[10], inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    # add a slash command called "prefix" that changes the prefix of the bot
    @discord.slash_command(name="prefix", description="Change the prefix of the prompt")
    async def prefix(self, ctx: discord.ApplicationContext, prefix: str = ""):
        debug(
            f"The user {ctx.author.name} ran the prefix command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        try:
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
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
            (prefix, ctx.guild.id),
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
    async def pretend(self, ctx: discord.ApplicationContext, pretend_to_be: str = ""):
        debug(
            f"The user {ctx.author} ran the pretend command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        try:
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
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
                (ctx.guild.id,),
            )
            con_data.commit()
            await ctx.respond("Pretend mode disabled", ephemeral=True, delete_after=5)
            await ctx.guild.me.edit(nick=None)
            return
        else:
            curs_data.execute(
                "UPDATE data SET pretend_enabled = 1 WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            con_data.commit()
            await ctx.respond("Pretend mode enabled", ephemeral=True, delete_after=5)
            # change the bots name on the server wit ctx.guild.me.edit(nick=pretend_to_be)
            await ctx.guild.me.edit(nick=pretend_to_be)
            curs_data.execute(
                "UPDATE data SET pretend_to_be = ? WHERE guild_id = ?",
                (pretend_to_be, ctx.guild.id),
            )
            con_data.commit()
            # if the usename is longer than 32 characters, shorten it
            if len(pretend_to_be) > 31:
                pretend_to_be = pretend_to_be[:32]
            await ctx.guild.me.edit(nick=pretend_to_be)
            return

    @discord.slash_command(name="enable_tts", description="Enable TTS when chatting")
    async def enable_tts(self, ctx: discord.ApplicationContext):
        # get the guild id
        guild_id = ctx.guild.id
        # connect to the database
        # update the tts value in the database
        curs_data.execute("UPDATE data SET tts = 1 WHERE guild_id = ?", (guild_id,))
        con_data.commit()
        # send a message
        await ctx.respond("TTS has been enabled", ephemeral=True)

    @discord.slash_command(name="disable_tts", description="Disable TTS when chatting")
    async def disable_tts(self, ctx: discord.ApplicationContext):
        # get the guild id
        guild_id = ctx.guild.id
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
        try:
            curs_data.execute("SELECT * FROM model WHERE guild_id = ?", (ctx.guild.id,))
            data = curs_data.fetchone()[1]
        except:
            data = None
        if data is None:
            curs_data.execute("INSERT INTO model VALUES (?, ?)", (ctx.guild.id, model))
        else:
            curs_data.execute(
                "UPDATE model SET model_name = ? WHERE guild_id = ?",
                (model, ctx.guild.id),
            )
        con_data.commit()
        await ctx.respond("Model changed !", ephemeral=True)

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
            curs_data.execute("SELECT * FROM images WHERE guild_id = ?", (ctx.guild.id,))
            data = curs_data.fetchone()
        except:
            data = None
        if enable_disable == "enable":
            enable_disable = 1
        elif enable_disable == "disable":
            enable_disable = 0
        if data is None:
            curs_data.execute(
                "INSERT INTO images VALUES (?, ?, ?)", (ctx.guild.id, 0, enable_disable)
            )
        else:
            curs_data.execute(
                "UPDATE images SET is_enabled = ? WHERE guild_id = ?",
                (enable_disable, ctx.guild.id),
            )
        con_data.commit()
        await ctx.respond(
            "Images recognition has been "
            + ("enabled" if enable_disable == 1 else "disabled"),
            ephemeral=True,
        )
