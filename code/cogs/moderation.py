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
        await ctx.respond("Our moderation capabilities have been switched to our new 100% free and open-source AI discord moderation bot! You add it to your server here: https://discord.com/api/oauth2/authorize?client_id=1071451913024974939&permissions=1377342450896&scope=bot and you can find the source code here: https://github.com/Paillat-dev/Moderator/ \n If you need help, you can join our support server here: https://discord.gg/pB6hXtUeDv", ephemeral=True)
        if enable == False:
            c.execute("DELETE FROM moderation WHERE guild_id = ?", (str(ctx.guild.id),))
            conn.commit()
            await ctx.respond("Moderation disabled!", ephemeral=True)
            return

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
        await ctx.respond("Our moderation capabilities have been switched to our new 100% free and open-source AI discord moderation bot! You add it to your server here: https://discord.com/api/oauth2/authorize?client_id=1071451913024974939&permissions=1377342450896&scope=bot and you can find the source code here: https://discord.gg/pB6hXtUeDv . If you need help, you can join our support server here: https://discord.gg/pB6hXtUeDv", ephemeral=True)

    @discord.slash_command(name="moderation_help", description="Get help with the moderation AI")
    @default_permissions(administrator=True)
    async def moderation_help(self, ctx: discord.ApplicationContext):
        await ctx.respond("Our moderation capabilities have been switched to our new 100% free and open-source AI discord moderation bot! You add it to your server here: https://discord.com/api/oauth2/authorize?client_id=1071451913024974939&permissions=1377342450896&scope=bot and you can find the source code here: https://github.com/Paillat-dev/Moderator/ . If you need help, you can join our support server here: https://discord.gg/pB6hXtUeDv", ephemeral=True)