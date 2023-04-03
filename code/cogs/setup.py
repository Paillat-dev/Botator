import discord
from config import debug, con_data, curs_data, con_premium, curs_premium


class Setup(discord.Cog):
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot

    @discord.slash_command(name="setup", description="Setup the bot")
    @discord.option(name="channel_id", description="The channel id", required=True)
    @discord.option(name="api_key", description="The api key", required=True)
    async def setup(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
        api_key: str,
    ):
        # check if the api key is valid
        debug(
            f"The user {ctx.author} ran the setup command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the channel is valid
        if channel is None:
            await ctx.respond("Invalid channel id", ephemeral=True)
            return
        # check if the guild is already in the database bi checking if there is a key for the guild
        try:
            curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
            data = curs_data.fetchone()
            if data[3] == None:
                data = None
        except:
            data = None

        if data != None:
            curs_data.execute(
                "UPDATE data SET channel_id = ?, api_key = ? WHERE guild_id = ?",
                (channel.id, api_key, ctx.guild.id),
            )
            #        c.execute("UPDATE data SET is_active = ?, max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (False, 64, 0.9, 0.0, 0.0, 5, ctx.guild.id))
            con_data.commit()
            await ctx.respond(
                "The channel id and the api key have been updated", ephemeral=True
            )
        else:
            # in this case, the guild is not in the database, so we add it
            curs_data.execute(
                "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ctx.guild.id,
                    channel.id,
                    api_key,
                    False,
                    64,
                    0.9,
                    0.0,
                    0.0,
                    0,
                    5,
                    "",
                    False,
                    "",
                    False,
                ),
            )
            con_data.commit()
            await ctx.respond(
                "The channel id and the api key have been added", ephemeral=True
            )

    @discord.slash_command(
        name="delete", description="Delete the information about this server"
    )
    ##@discord.commands.permissions(administrator=True)
    async def delete(self, ctx: discord.ApplicationContext):
        debug(
            f"The user {ctx.author} ran the delete command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # delete the guild from the database, except the guild id and the uses_count_today
        curs_data.execute(
            "UPDATE data SET api_key = ?, channel_id = ?, is_active = ?, max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?",
            (None, None, False, 50, 0.9, 0.0, 0.0, 0, ctx.guild.id),
        )
        con_data.commit()
        await ctx.respond("Deleted", ephemeral=True)

    # create a command called "enable" that only admins can use
    @discord.slash_command(name="enable", description="Enable the bot")
    ##@discord.commands.permissions(administrator=True)
    async def enable(self, ctx: discord.ApplicationContext):
        # if the guild is eqal to 1014156298226515970, the guild is banned
        if ctx.guild.id == 1014156298226515970:
            await ctx.respond(
                "This server is banned for bad and nsfw use.", ephemeral=True
            )
            return
        # check if the guild is in the database
        debug(
            f"The user {ctx.author} ran the enable command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # enable the guild
        curs_data.execute(
            "UPDATE data SET is_active = ? WHERE guild_id = ?", (True, ctx.guild.id)
        )
        con_data.commit()
        await ctx.respond("Enabled", ephemeral=True)

    # create a command called "disable" that only admins can use
    @discord.slash_command(name="disable", description="Disable the bot")
    ##@discord.commands.permissions(administrator=True)
    async def disable(self, ctx: discord.ApplicationContext):
        debug(
            f"The user {ctx.author} ran the disable command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # disable the guild
        curs_data.execute(
            "UPDATE data SET is_active = ? WHERE guild_id = ?", (False, ctx.guild.id)
        )
        con_data.commit()
        await ctx.respond("Disabled", ephemeral=True)

    # create a command calles "add channel" that can only be used in premium servers
    @discord.slash_command(
        name="add_channel",
        description="Add a channel to the list of channels. Premium only.",
    )
    @discord.option(
        name="channel",
        description="The channel to add",
        type=discord.TextChannel,
        required=False,
    )
    async def add_channel(
        self, ctx: discord.ApplicationContext, channel: discord.TextChannel = None
    ):
        debug(
            f"The user {ctx.author} ran the add_channel command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # check if the guild is premium
        try:
            con_premium.execute("SELECT premium FROM data WHERE guild_id = ?", (ctx.guild.id,))
            premium = con_premium.fetchone()[0]
        except:
            premium = 0
        if not premium:
            await ctx.respond("This server is not premium", ephemeral=True)
            return
        if channel is None:
            channel = ctx.channel
        # check if the channel is already in the list
        curs_data.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if str(channel.id) == curs_data.fetchone()[0]:
            await ctx.respond(
                "This channel is already set as the main channel", ephemeral=True
            )
            return
        con_premium.execute("SELECT * FROM channels WHERE guild_id = ?", (ctx.guild.id,))
        guild_channels = con_premium.fetchone()
        if guild_channels is None:
            # if the channel is not in the list, add it
            con_premium.execute(
                "INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?)",
                (ctx.guild.id, channel.id, None, None, None, None),
            )
            con_premium.commit()
            await ctx.respond(f"Added channel **{channel.name}**", ephemeral=True)
            return
        channels = guild_channels[1:]
        if str(channel.id) in channels:
            await ctx.respond("This channel is already added", ephemeral=True)
            return
        for i in range(5):
            if channels[i] == None:
                con_premium.execute(
                    f"UPDATE channels SET channel{i} = ? WHERE guild_id = ?",
                    (channel.id, ctx.guild.id),
                )
                con_premium.commit()
                await ctx.respond(f"Added channel **{channel.name}**", ephemeral=True)
                return
        await ctx.respond("You can only add 5 channels", ephemeral=True)

    # create a command called "remove channel" that can only be used in premium servers
    @discord.slash_command(
        name="remove_channel",
        description="Remove a channel from the list of channels. Premium only.",
    )
    @discord.option(
        name="channel",
        description="The channel to remove",
        type=discord.TextChannel,
        required=False,
    )
    async def remove_channel(
        self, ctx: discord.ApplicationContext, channel: discord.TextChannel = None
    ):
        debug(
            f"The user {ctx.author} ran the remove_channel command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}"
        )
        # check if the guild is in the database
        curs_data.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if curs_data.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        # check if the guild is premium
        try:
            con_premium.execute("SELECT premium FROM data WHERE guild_id = ?", (ctx.guild.id,))
            premium = con_premium.fetchone()[0]
        except:
            premium = 0
        if not premium:
            await ctx.respond("This server is not premium", ephemeral=True)
            return
        if channel is None:
            channel = ctx.channel
        # check if the channel is in the list
        con_premium.execute("SELECT * FROM channels WHERE guild_id = ?", (ctx.guild.id,))
        guild_channels = con_premium.fetchone()
        curs_data.execute("SELECT channel_id FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if str(channel.id) == curs_data.fetchone()[0]:
            await ctx.respond(
                "This channel is set as the main channel and therefore cannot be removed. Type /setup to change the main channel.",
                ephemeral=True,
            )
            return
        if guild_channels is None:
            await ctx.respond(
                "This channel was not added. Nothing changed", ephemeral=True
            )
            return
        channels = guild_channels[1:]
        if str(channel.id) not in channels:
            await ctx.respond(
                "This channel was not added. Nothing changed", ephemeral=True
            )
            return
        # remove the channel from the list
        for i in range(5):
            if channels[i] == str(channel.id):
                con_premium.execute(
                    f"UPDATE channels SET channel{i} = ? WHERE guild_id = ?",
                    (None, ctx.guild.id),
                )
                con_premium.commit()
                await ctx.respond(f"Removed channel **{channel.name}**", ephemeral=True)
                return
