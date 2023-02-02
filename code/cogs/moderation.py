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
    #we set the default permissions to the administrator permission, so only the server administrators can use this command
    @default_permissions(administrator=True)
    async def moderation(self, ctx: discord.ApplicationContext, enable: bool, log_channel: discord.TextChannel, moderator_role: discord.Role):
        try: 
            data = c.execute("SELECT * FROM moderation WHERE guild_id = ?", (str(ctx.guild.id),))
            data = c.fetchone()
        except: data = None
        if data is None:
            c.execute("INSERT INTO moderation VALUES (?, ?, ?, ?)", (str(ctx.guild.id), str(log_channel.id), enable, str(moderator_role.id)))
            conn.commit()
        else:
            c.execute("UPDATE moderation SET logs_channel_id = ?, is_enabled = ? WHERE guild_id = ?", (str(log_channel.id), enable, str(ctx.guild.id)))
            conn.commit()
        await ctx.respond("Successfully updated moderation settings for this server", ephemeral=True)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user: return
        try: c.execute("SELECT * FROM moderation WHERE guild_id = ?", (str(message.guild.id),))
        except: return
        data = c.fetchone()
        channel = self.bot.get_channel(int(data[1]))
        is_enabled = data[2]
        moderator_role = message.guild.get_role(int(data[3]))
        #we also do that with the manage_messages permission, so the moderators can't be moderated
        if message.author.guild_permissions.manage_messages: return #if the user is a moderator, we don't want to moderate him because he is allowed to say whatever he wants because he is just like a dictator
        if message.author.guild_permissions.administrator: return #if the user is an administrator, we don't want to moderate him because he is allowed to say whatever he wants because he is a DICTATOR
        if not is_enabled: return
        content = message.content
        message_toxicity = tox.get_toxicity(content)
        if message_toxicity >= 0.40:
            await message.delete()
            embed = discord.Embed(title="Message deleted", description=f"{message.author.mention} Your message was deleted because it was too toxic. Please keep this server safe and friendly. If you think this was a mistake, please contact a moderator.", color=discord.Color.red())
            await message.channel.send(f"{message.author.mention}", embed=embed, delete_after=15)
            formatted_message_sent_date = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
            embed = discord.Embed(title="Message deleted", description=f"The message \n***{content}***\n of {message.author.mention} sent in {message.channel.mention} on date **{formatted_message_sent_date}** was deleted because it was too toxic. The toxicity score was of **{message_toxicity}**", color=discord.Color.red())
            await channel.send(embed=embed)
        elif 0.37 < message_toxicity < 0.40: #if the message is not toxic, but it is close to being toxic, we send a warning
            embed = discord.Embed(title="Possible toxic message", description=f"A possible [toxic message: **{content}**]({message.jump_url}) was sent by {message.author.mention} in {message.channel.mention}. Please check it out.", color=discord.Color.orange())
            await channel.send(embed=embed)
            #we also reac with an orange circle emoji to the message
            await message.add_reaction("🟠")
            #we reply to the message with a ping to the moderators
            moderator_role = message.guild.get_role(int(data[3]))
            await message.reply(f"Hey {moderator_role.mention}, this message might be toxic. Please check it out.", mention_author=False, delete_after=15)
        else:
            #the message is not toxic, so we don't do anything
            pass

    @discord.slash_command(name="get_toxicity", description="Get the toxicity of a message")
    @discord.option(name="message", description="The message you want to check", required=True)
    @default_permissions(administrator=True)
    async def get_toxicity(self, ctx: discord.ApplicationContext, message: str):
        toxicity = tox.get_toxicity(message)
        await ctx.respond(f"The toxicity of the message **{message}** is **{toxicity}**")
