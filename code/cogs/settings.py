import discord
from config import debug, conn, c

class Settings (discord.Cog) :
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    #create a command called "advanced" that only admins can use, wich sets the advanced settings up: max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size
    @discord.slash_command(name="advanced", description="Advanced settings")
    ##@discord.commands.permissions(administrator=True)
    #add the options
    @discord.option(name="max_tokens", description="The max tokens", required=False)
    @discord.option(name="temperature", description="The temperature", required=False)
    @discord.option(name="frequency_penalty", description="The frequency penalty", required=False)
    @discord.option(name="presence_penalty", description="The presence penalty", required=False)
    @discord.option(name="prompt_size", description="The prompt size", required=False)
    async def advanced(self, ctx: discord.ApplicationContext, max_tokens: int = None, temperature: float = None, frequency_penalty: float = None, presence_penalty: float = None, prompt_size: int = None):
        debug(f"The user {ctx.author} ran the advanced command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        #check if the user has entered at least one argument
        if max_tokens is None and temperature is None and frequency_penalty is None and presence_penalty is None and prompt_size is None:
            await ctx.respond("You must enter at least one argument", ephemeral=True)
            return
        #check if the user has entered valid arguments
        if max_tokens is not None and (max_tokens < 1 or max_tokens > 2048):
            await ctx.respond("Invalid max tokens", ephemeral=True)
            return
        if temperature is not None and (temperature < 0.0 or temperature > 1.0):
            await ctx.respond("Invalid temperature", ephemeral=True)
            return
        if frequency_penalty is not None and (frequency_penalty < 0.0 or frequency_penalty > 2.0):
            await ctx.respond("Invalid frequency penalty", ephemeral=True)
            return
        if presence_penalty is not None and (presence_penalty < 0.0 or presence_penalty > 2.0):
            await ctx.respond("Invalid presence penalty", ephemeral=True)
            return
        if prompt_size is not None and (prompt_size < 1 or prompt_size > 10):
            await ctx.respond("Invalid prompt size", ephemeral=True)
            return
        if max_tokens is None:
            if c.execute("SELECT max_tokens FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0] is not None and max_tokens is None:
                max_tokens = c.execute("SELECT max_tokens FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
            else:
                max_tokens = 64
        if temperature is None:
            if c.execute("SELECT temperature FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0] is not None and temperature is None:
                temperature = c.execute("SELECT temperature FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
            else:
                temperature = 0.5
        if frequency_penalty is None:
            if c.execute("SELECT frequency_penalty FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0] is not None and frequency_penalty is None:
                frequency_penalty = c.execute("SELECT frequency_penalty FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
            else:
                frequency_penalty = 0.0
        if presence_penalty is None:
            if c.execute("SELECT presence_penalty FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0] is not None and presence_penalty is None:
                presence_penalty = c.execute("SELECT presence_penalty FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
            else:
                presence_penalty = 0.0
        if prompt_size is None:
            if c.execute("SELECT prompt_size FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0] is not None and prompt_size is None:
                prompt_size = c.execute("SELECT prompt_size FROM data WHERE guild_id = ?", (ctx.guild.id,)).fetchone()[0]
            else:
                prompt_size = 1
        #update the database
        c.execute("UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size, ctx.guild.id))
        conn.commit()
        await ctx.respond("Advanced settings updated", ephemeral=True)
        #create a command called "delete" that only admins can use wich deletes the guild id, the api key, the channel id and the advanced settings from the database

    @discord.slash_command(name="default", description="Default settings")
    ##@discord.commands.permissions(administrator=True)
    async def default(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author} ran the default command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            await ctx.respond("This server is not setup, please run /setup", ephemeral=True)
            return
        #set the advanced settings (max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size) and also prompt_prefix to their default values
        c.execute("UPDATE data SET max_tokens = ?, temperature = ?, frequency_penalty = ?, presence_penalty = ?, prompt_size = ? WHERE guild_id = ?", (64, 0.9, 0.0, 0.0, 5, ctx.guild.id))
        conn.commit()
        await ctx.respond("The advanced settings have been set to their default values", ephemeral=True)
    #create a command called "cancel" that deletes the last message sent by the bot in the response channel

    #when a message is sent into a channel check if the guild is in the database and if the bot is enabled
    @discord.slash_command(name="info", description="Show the information stored about this server")
    async def info(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author} ran the info command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        #this command sends all the data about the guild, including the api key, the channel id, the advanced settings
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        #get all the data from the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        data = c.fetchone()
        #send the data
        embed = discord.Embed(title="Info", description="Here is the info page", color=0x00ff00)
        embed.add_field(name="guild_id", value=data[0], inline=False)
        embed.add_field(name="API Key", value=data[2], inline=False)
        embed.add_field(name="Channel ID", value=data[1], inline=False)
        embed.add_field(name="Is Active", value=data[3], inline=False)
        embed.add_field(name="Max Tokens", value=data[4], inline=False)
        embed.add_field(name="Temperature", value=data[5], inline=False)
        embed.add_field(name="Frequency Penalty", value=data[6], inline=False)
        embed.add_field(name="Presence Penalty", value=data[7], inline=False)
        embed.add_field(name="Prompt Size", value=data[9], inline=False)
        if data[10]:
            embed.add_field(name="Prompt prefix", value=data[10], inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    #add a slash command called "prefix" that changes the prefix of the bot
    @discord.slash_command(name="prefix", description="Change the prefix of the prompt")
    async def prefix(self, ctx: discord.ApplicationContext, prefix: str):
        debug(f"The user {ctx.author.name} ran the prefix command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        await ctx.respond("Prefix changed !", ephemeral=True)
        c.execute("UPDATE data SET prompt_prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        conn.commit()

    #when someone mentions the bot, check if the guild is in the database and if the bot is enabled. If it is, send a message answering the mention
    @discord.slash_command(name="pretend", description="Make the bot pretend to be someone else")
    @discord.option(name="pretend to be...", description="The person/thing you want the bot to pretend to be. Leave blank to disable pretend mode", required=False)
    async def pretend(self, ctx: discord.ApplicationContext, pretend_to_be: str = None):
        debug(f"The user {ctx.author} ran the pretend command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            await ctx.respond("This server is not setup", ephemeral=True)
            return
        #check if the bot is enabled
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone()[3] == 0:
            await ctx.respond("The bot is disabled", ephemeral=True)
            return
        if pretend_to_be is (None or "off" or "stfu"):
            pretend_to_be = ""
            c.execute("UPDATE data SET pretend_enabled = 0 WHERE guild_id = ?", (ctx.guild.id,))
            conn.commit()
            await ctx.respond("Pretend mode disabled", ephemeral=True)
            await ctx.guild.me.edit(nick=None)
            return
        else:
            c.execute("UPDATE data SET pretend_enabled = 1 WHERE guild_id = ?", (ctx.guild.id,))
            conn.commit()
            await ctx.respond("Pretend mode enabled", ephemeral=True)
            #change the bots name on the server wit ctx.guild.me.edit(nick=pretend_to_be)
            await ctx.guild.me.edit(nick=pretend_to_be)
            c.execute("UPDATE data SET pretend_to_be = ? WHERE guild_id = ?", (pretend_to_be, ctx.guild.id))
            conn.commit()
            await ctx.guild.me.edit(nick=pretend_to_be)
            return

    @discord.slash_command(name="enable_tts", description="Enable TTS when chatting")
    async def enable_tts(self, ctx: discord.ApplicationContext):
        #get the guild id
        guild_id = ctx.guild.id
        #connect to the database
        #update the tts value in the database
        c.execute("UPDATE data SET tts = 1 WHERE guild_id = ?", (guild_id,))
        conn.commit()
        #send a message
        await ctx.respond("TTS has been enabled", ephemeral=True)

    @discord.slash_command(name="disable_tts", description="Disable TTS when chatting")
    async def disable_tts(self, ctx: discord.ApplicationContext):
        #get the guild id
        guild_id = ctx.guild.id
        #connect to the database
        #update the tts value in the database
        c.execute("UPDATE data SET tts = 0 WHERE guild_id = ?", (guild_id,))
        conn.commit()
        #send a message
        await ctx.respond("TTS has been disabled", ephemeral=True)

