import discord
import re
import os


class ManageChat(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.slash_command(
        name="clear", description="Clear all the messages in the channel"
    )
    async def clear(self, ctx: discord.ApplicationContext):
        await ctx.respond("messages deleted!", ephemeral=True)
        return await ctx.channel.purge()

    @discord.slash_command(
        name="transcript",
        description="Get a transcript of the messages that have been sent in this channel intoa text file",
    )
    @discord.option(
        name="channel_send",
        description="The channel to send the transcript to",
        required=False,
    )
    async def transcript(
        self, ctx: discord.ApplicationContext, channel_send: discord.TextChannel = None
    ):
        # save all the messages in the channel in a txt file and send it
        messages = await ctx.channel.history(limit=None).flatten()
        messages.reverse()
        transcript = ""
        # defer the response
        await ctx.defer()  # defer the response so that the bot doesn't say that it's thinking
        for msg in messages:
            if msg.author.bot:
                transcript += f"Botator: {msg.content}\n"
            else:
                mentions = re.findall(r"<@!?\d+>", msg.content)
                # then replace each mention with the name of the user
                for mention in mentions:
                    # get the user id
                    id = mention[2:-1]
                    # get the user
                    user = await self.bot.fetch_user(id)
                    # replace the mention with the name
                    msg.content = msg.content.replace(
                        mention, msg.guild.get_member(user.id).name
                    )
                transcript += f"{msg.author.name}: {msg.content}\n"
        # save the transcript in a txt file called transcript.txt. If the file already exists, delete it and create a new one
        # check if the file exists
        if os.path.exists("transcript.txt"):
            os.remove("transcript.txt")
        f = open("transcript.txt", "w")
        f.write(transcript)
        f.close()
        last_message: discord.Message = await ctx.channel.fetch_message(
            ctx.channel.last_message_id
        )
        new_file_name = f"transcript_{ctx.guild.name}_{ctx.channel.name}_{last_message.created_at.strftime('%d-%B-%Y')}.txt"
        # rename the file with the name of the channel and the date in this format: transcript_servername_channelname_dd-month-yyyy.txt ex : transcript_Botator_Testing_12-may-2021.txt
        os.rename(
            "transcript.txt",
            new_file_name,
        )
        # send the file in a private message to the user who ran the command
        # TODO: rework so as to give the choice of a private send or a public send
        if channel_send is None:
            await ctx.respond(
                file=discord.File(new_file_name),
                ephemeral=True,
            )
        else:
            await channel_send.send(file=discord.File(new_file_name))
            await ctx.respond("Transcript sent!", ephemeral=True, delete_after=5)
        await ctx.author.send(file=discord.File(new_file_name))
        # delete the file
        os.remove(new_file_name)
