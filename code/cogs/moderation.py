import discord
from discord import default_permissions
import os
from config import debug, c, conn
import openai
import requests
import toxicity as tox #this is a file called toxicity.py, which contains the toxicity function that allows you to check if a message is toxic or not (it uses the perspective api)
class Moderation (discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot
    @discord.slash_command(name="moderation", description="Enable or disable AI moderation & set the rules")
    @discord.option(name="enable", description="Enable or disable AI moderation", reqired=True,)
    @discord.option(name="log_channel", description="The channel where the moderation logs will be sent", required=True)
    @discord.option(name="moderator_role", description="The role of the moderators", required=True)
    #the types of toxicity are     'requestedAttributes': {'TOXICITY': {}, 'SEVERE_TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'INSULT': {}, 'PROFANITY': {}, 'THREAT': {}, 'SEXUALLY_EXPLICIT': {}, 'FLIRTATION': {}, 'OBSCENE': {}, 'SPAM': {}},
    @discord.option(name="toxicity", description="The toxicity threshold", required=False)
    @discord.option(name="severe_toxicity", description="The severe toxicity threshold", required=False)
    @discord.option(name="identity_attack", description="The identity attack threshold", required=False)
    @discord.option(name="insult", description="The insult threshold", required=False)
    @discord.option(name="profanity", description="The profanity threshold", required=False)
    @discord.option(name="threat", description="The threat threshold", required=False)
    @discord.option(name="sexually_explicit", description="The sexually explicit threshold", required=False)
    @discord.option(name="flirtation", description="The flirtation threshold", required=False)
    @discord.option(name="obscene", description="The obscene threshold", required=False)
    @discord.option(name="spam", description="The spam threshold", required=False)
    #we set the default permissions to the administrator permission, so only the server administrators can use this command
    @default_permissions(administrator=True)
    async def moderation(self, ctx: discord.ApplicationContext, enable: bool, log_channel: discord.TextChannel, moderator_role: discord.Role, toxicity: float = None, severe_toxicity: float = None, identity_attack: float = None, insult: float = None, profanity: float = None, threat: float = None, sexually_explicit: float = None, flirtation: float = None, obscene: float = None, spam: float = None):
        try: 
            data = c.execute("SELECT * FROM moderation WHERE guild_id = ?", (str(ctx.guild.id),))
            data = c.fetchone()
        except: data = None
        if data is None:
            #first we check if any of the values is none. If it's none, we set it to 0.40
            if toxicity is None: toxicity = 0.40
            if severe_toxicity is None: severe_toxicity = 0.40
            if identity_attack is None: identity_attack = 0.40
            if insult is None: insult = 0.40
            if profanity is None: profanity = 0.40
            if threat is None: threat = 0.40
            if sexually_explicit is None: sexually_explicit = 0.40
            if flirtation is None: flirtation = 0.40
            if obscene is None: obscene = 0.40
            if spam is None: spam = 0.40
            c.execute("INSERT INTO moderation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(ctx.guild.id), str(log_channel.id), enable, str(moderator_role.id), toxicity, severe_toxicity, identity_attack, insult, profanity, threat, sexually_explicit, flirtation, obscene, spam))
            conn.commit()
            await ctx.respond(content="Moderation has been enabled!", ephemeral=True)
        else:
            #for each value we check if it's none. If it's none and there's no value in the database, we set it to 0.40, otherwise we set it to the value in the database
            if toxicity is None and data[4] is not None: toxicity = data[4]
            elif toxicity is None and data[4] is None: toxicity = 0.40
            if severe_toxicity is None and data[5] is not None: severe_toxicity = data[5]
            elif severe_toxicity is None and data[5] is None: severe_toxicity = 0.40
            if identity_attack is None and data[6] is not None: identity_attack = data[6]
            elif identity_attack is None and data[6] is None: identity_attack = 0.40
            if insult is None and data[7] is not None: insult = data[7]
            elif insult is None and data[7] is None: insult = 0.40
            if profanity is None and data[8] is not None: profanity = data[8]
            elif profanity is None and data[8] is None: profanity = 0.40
            if threat is None and data[9] is not None: threat = data[9]
            elif threat is None and data[9] is None: threat = 0.40
            if sexually_explicit is None and data[10] is not None: sexually_explicit = data[10]
            elif sexually_explicit is None and data[10] is None: sexually_explicit = 0.40
            if flirtation is None and data[11] is not None: flirtation = data[11]
            elif flirtation is None and data[11] is None: flirtation = 0.40
            if obscene is None and data[12] is not None: obscene = data[12]
            elif obscene is None and data[12] is None: obscene = 0.40
            if spam is None and data[13] is not None: spam = data[13]
            elif spam is None and data[13] is None: spam = 0.40
            c.execute("UPDATE moderation SET logs_channel_id = ?, is_enabled = ?, mod_role_id = ?, toxicity = ?, severe_toxicity = ?, identity_attack = ?, insult = ?, profanity = ?, threat = ?, sexually_explicit = ?, flirtation = ?, obscene = ?, spam = ? WHERE guild_id = ?", (str(log_channel.id), enable, str(moderator_role.id), toxicity, severe_toxicity, identity_attack, insult, profanity, threat, sexually_explicit, flirtation, obscene, spam, str(ctx.guild.id)))
            conn.commit()
        await ctx.respond("Successfully updated moderation settings for this server", ephemeral=True)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user: return
        try: c.execute("SELECT * FROM moderation WHERE guild_id = ?", (str(message.guild.id),))
        except: return
        data = c.fetchone()
        if data is None: return
        channel = self.bot.get_channel(int(data[1]))
        is_enabled = data[2]
        moderator_role = message.guild.get_role(int(data[3]))
        #we also do that with the manage_messages permission, so the moderators can't be moderated
        if message.author.guild_permissions.manage_messages: return #if the user is a moderator, we don't want to moderate him because he is allowed to say whatever he wants because he is just like a dictator
        if message.author.guild_permissions.administrator: return #if the user is an administrator, we don't want to moderate him because he is allowed to say whatever he wants because he is a DICTATOR
        if not is_enabled: return
        content = message.content
        message_toxicity = tox.get_toxicity(content)
        reasons_to_delete = []
        reasons_to_suspicous = []
        for i in message_toxicity: 
            if i >= float(data[message_toxicity.index(i)+4]): reasons_to_delete.append(tox.toxicity_names[message_toxicity.index(i)])
        for i in message_toxicity:
            if float(data[message_toxicity.index(i)+4]-0.1) <= i < float(data[message_toxicity.index(i)+4]): reasons_to_suspicous.append(tox.toxicity_names[message_toxicity.index(i)])
        if len(reasons_to_delete) > 0:
            embed = discord.Embed(title="Message deleted", description=f"Your message was deleted because it was too toxic. The following reasons were found: **{'**, **'.join(reasons_to_delete)}**", color=discord.Color.red())
            await message.reply(f"{message.author.mention}", embed=embed, delete_after=15)
            await message.delete()
            embed = discord.Embed(title="Message deleted", description=f"**{message.author}**'s message ***{content}*** was deleted because it was too toxic. The following reasons were found:", color=discord.Color.red())
            for i in reasons_to_delete:
                toxicity_value = message_toxicity[tox.toxicity_names.index(i)]
                embed.add_field(name=i, value=f"Found toxicity value: **{toxicity_value*100}%**", inline=False)
            await channel.send(embed=embed)
        elif len(reasons_to_suspicous) > 0:
            await message.reply(f"{moderator_role.mention} This message might be toxic. The following reasons were found: **{'**, **'.join(reasons_to_suspicous)}**", delete_after=15, mention_author=False)
            embed = discord.Embed(title="Message suspicious", description=f"**{message.author}**'s message [***{content}***]({message.jump_url}) might be toxic. The following reasons were found:", color=discord.Color.orange())
            for i in reasons_to_suspicous:
                toxicity_value = message_toxicity[tox.toxicity_names.index(i)]
                embed.add_field(name=i, value=f"Found toxicity value: **{toxicity_value*100}%**", inline=False)
            await channel.send(embed=embed)
            #we add a reaction to the message so the moderators can easily find it orange circle emoji
            await message.add_reaction("🟠")

    @discord.slash_command(name="get_toxicity", description="Get the toxicity of a message")
    @discord.option(name="message", description="The message you want to check", required=True)
    @default_permissions(administrator=True)
    async def get_toxicity(self, ctx: discord.ApplicationContext, message: str):
        response = tox.get_toxicity(message)
#        try: toxicity, severe_toxicity, identity_attack, insult, profanity, threat, sexually_explicit, flirtation, obscene, spam = response
#       except: toxicity, severe_toxicity, identity_attack, insult, profanity, threat = response
        would_have_been_deleted = []
        would_have_been_suspicous = []
        c.execute("SELECT * FROM moderation WHERE guild_id = ?", (str(ctx.guild.id),))
        data = c.fetchone()
        for i in response:
            if i >= float(data[response.index(i)+4]):
                would_have_been_deleted.append(tox.toxicity_names[response.index(i)])
            elif i >= float(data[response.index(i)+4])-0.1:
                would_have_been_suspicous.append(tox.toxicity_names[response.index(i)])
        if would_have_been_deleted !=[]: embed = discord.Embed(title="Toxicity", description=f"Here are the different toxicity scores of the message\n***{message}***", color=discord.Color.red())
        elif would_have_been_suspicous !=[] and would_have_been_deleted ==[]: embed = discord.Embed(title="Toxicity", description=f"Here are the different toxicity scores of the message\n***{message}***", color=discord.Color.orange())
        else: embed = discord.Embed(title="Toxicity", description=f"Here are the different toxicity scores of the message\n***{message}***", color=discord.Color.green())
        for i in response: embed.add_field(name=tox.toxicity_names[response.index(i)], value=f"{str( float(i)*100)}%", inline=False)
        if would_have_been_deleted != []: embed.add_field(name="Would have been deleted", value=f"Yes, the message would have been deleted because of the following toxicity scores: **{'**, **'.join(would_have_been_deleted)}**", inline=False)
        if would_have_been_suspicous != [] and would_have_been_deleted == []: embed.add_field(name="Would have been marked as suspicious", value=f"Yes, the message would have been marked as suspicious because of the following toxicity scores: {', '.join(would_have_been_suspicous)}", inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="moderation_help", description="Get help with the moderation AI")
    async def moderation_help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Moderation AI help", description="Here is a list of all the moderation commands", color=discord.Color.blurple())
        for definition in tox.toxicity_definitions:
            embed.add_field(name=tox.toxicity_names[tox.toxicity_definitions.index(definition)], value=definition, inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
