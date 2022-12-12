import discord
import re
import os
from config import debug, c

class ManageChat (discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.slash_command(name="cancel", description="Cancel the last message sent into a channel")
    async def cancel(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author} ran the cancel command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (ctx.guild.id,))
        if c.fetchone() is None:
            await ctx.respond("This server is not setup, please run /setup", ephemeral=True)
            return
        #get the last message sent by the bot in the cha where the command was sent
        last_message = await ctx.channel.fetch_message(ctx.channel.last_message_id)
        #delete the message
        await last_message.delete()
        await ctx.respond("The last message has been deleted", ephemeral=True)

    #add a slash command called "clear" that deletes all the messages in the channel
    @discord.slash_command(name="clear", description="Clear all the messages in the channel")
    async def clear(self, ctx: discord.ApplicationContext):
        debug(f"The user {ctx.author.display_name} ran the clear command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        await ctx.respond("messages deleted!", ephemeral=True)
        return await ctx.channel.purge()

    @discord.slash_command(name="transcript", description="Get a transcript of the messages that have been sent in this channel intoa text file")
    @discord.option(name="channel_send", description="The channel to send the transcript to", required=False)
    async def transcript(self, ctx: discord.ApplicationContext, channel_send: discord.TextChannel = None):
        debug(f"The user {ctx.author.display_name} ran the transcript command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
    #save all the messages in the channel in a txt file and send it
        messages = await ctx.channel.history(limit=None).flatten()
        messages.reverse()
        transcript = ""
        #defer the response
        await ctx.defer() #defer the response so that the bot doesn't say that it's thinking 
        for msg in messages:
            if msg.author.bot:
                transcript += f"Botator: {msg.content}\n"
            else:
                mentions = re.findall(r"<@!?\d+>", msg.content)
                #then replace each mention with the name of the user
                for mention in mentions:
                    #get the user id
                    id = mention[2:-1]
                    #get the user
                    user = await self.bot.fetch_user(id)
                    #replace the mention with the name
                    msg.content = msg.content.replace(mention, msg.guild.get_member(user.id).display_name)
                transcript += f"{msg.author.display_name}: {msg.content}\n"
    #save the transcript in a txt file called transcript.txt. If the file already exists, delete it and create a new one
    #check if the file exists
        if os.path.exists("transcript.txt"):
            os.remove("transcript.txt")
        f = open("transcript.txt", "w")
        f.write(transcript)
        f.close()
        last_message: discord.Message = await ctx.channel.fetch_message(ctx.channel.last_message_id)
        #rename the file with the name of the channel and the date in this format: transcript_servername_channelname_dd-month-yyyy.txt ex : transcript_Botator_Testing_12-may-2021.txt
        os.rename("transcript.txt", f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt")
    #send the file in a private message to the user who ran the command
        if channel_send is None:
            await ctx.respond(file=discord.File(f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt"), ephemeral=True)
        else:
            await channel_send.send(file=discord.File(f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt"))
            await ctx.respond("Transcript sent!", ephemeral=True, delete_after=5)
        await ctx.author.send(file=discord.File(f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt"))
    #delete the file
        os.remove(f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt")