import discord
from discord.ext import commands
from config import debug, curs_data, max_uses, curs_premium, con_data, con_premium, webhook_url
import makeprompt as mp
import aiohttp


class MyModal(discord.ui.Modal):
    def __init__(self, message):
        super().__init__(title="Downvote")
        self.add_item(
            discord.ui.InputText(label="Reason", style=discord.InputTextStyle.long)
        )
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        debug("Downvote sent !")
        embed = discord.Embed(
            title="Thanks for your feedback !",
            description="Your downvote has been sent to the developers. Thanks for your help !",
            color=discord.Color.og_blurple(),
        )
        embed.add_field(name="Message", value=self.children[0].value)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        if webhook_url != "" and webhook_url != None:
            session = aiohttp.ClientSession()
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            embed = discord.Embed(
                title="Downvote",
                description=f"Downvote recieved!",
                color=discord.Color.og_blurple(),
            )
            embed.add_field(name="Reason", value=self.children[0].value, inline=True)
            embed.add_field(name="Author", value=interaction.user.mention, inline=True)
            embed.add_field(
                name="Channel", value=self.message.channel.name, inline=True
            )
            embed.add_field(name="Guild", value=self.message.guild.name, inline=True)
            history = await self.message.channel.history(
                limit=5, before=self.message
            ).flatten()
            history.reverse()
            users = []
            fake_users = []
            for user in history:
                if user.author not in users:
                    # we anonimize the user, so user1, user2, user3, etc
                    fake_users.append(f"user{len(fake_users)+1}")
                    users.append(user.author)
            if self.message.author not in users:
                fake_users.append(f"user{len(fake_users)+1}")
                users.append(self.message.author)
            for msg in history:
                uname = fake_users[users.index(msg.author)]

                if len(msg.content) > 1023:
                    embed.add_field(
                        name=f"{uname} said", value=msg.content[:1023], inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{uname} said", value=msg.content, inline=False
                    )
            if len(self.message.content) > 1021:
                uname = fake_users[users.index(self.message.author)]
                embed.add_field(
                    name=f"{uname} said",
                    value="*" + self.message.content[:1021] + "*",
                    inline=False,
                )
            else:
                uname = fake_users[users.index(self.message.author)]
                embed.add_field(
                    name=f"{uname} said",
                    value="*" + self.message.content + "*",
                    inline=False,
                )
            await webhook.send(embed=embed)
        else:
            debug(
                "Error while sending webhook, probably no webhook is set up in the .env file"
            )


class Chat(discord.Cog):
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        await mp.chat_process(self, message)

    @discord.slash_command(name="say", description="Say a message")
    async def say(self, ctx: discord.ApplicationContext, message: str):
        await ctx.respond("Message sent !", ephemeral=True)
        await ctx.send(message)

    @discord.slash_command(name="redo", description="Redo a message")
    async def redo(self, ctx: discord.ApplicationContext):
        history = await ctx.channel.history(limit=2).flatten()
        message_to_delete = history[0]
        message_to_redo = history[1]
        if message_to_delete.author.id == self.bot.user.id:
            await message_to_delete.delete()
        else:
            message_to_redo = history[0]
        await ctx.respond("Message redone !", ephemeral=True)
        await mp.chat_process(self, message_to_redo)

    @discord.message_command(name="Downvote", description="Downvote a message")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def downvote(self, ctx: discord.ApplicationContext, message: discord.Message):
        if message.author.id == self.bot.user.id:
            modal = MyModal(message)
            await ctx.send_modal(modal)
        else:
            await ctx.respond(
                "You can't downvote a message that is not from me !", ephemeral=True
            )

    @downvote.error
    async def downvote_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond("You are on cooldown !", ephemeral=True)
        else:
            debug(error)
            raise error
