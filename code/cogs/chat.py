import discord
from config import debug, c, max_uses, cp, conn, connp, webhook_url
import makeprompt as mp
import aiohttp

class MyModal(discord.ui.Modal):
    def __init__(self, message):
        super().__init__(title="Downvote")
        self.add_item(discord.ui.InputText(label="Reason", style=discord.InputTextStyle.long))
        self.message = message

    async def callback(self, interaction: discord.Interaction):
        debug("Downvote sent !")
        embed = discord.Embed(title="Thanks for your feedback !", description="Your downvote has been sent to the developers. Thanks for your help !", color=discord.Color.og_blurple())
        embed.add_field(name="Message", value=self.children[0].value)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        try: 
            session = aiohttp.ClientSession()
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            embed = discord.Embed(title="Downvote", description=f"Downvote recieved!", color=discord.Color.og_blurple())
            embed.add_field(name="Reason", value=self.children[0].value)
            embed.add_field(name="Author", value=self.message.author.mention)
            embed.add_field(name="Channel", value=self.message.channel.name)
            embed.add_field(name="Guild", value=self.message.guild.name)
            msgembed = discord.Embed(title="Messages", description=f"Messages history", color=discord.Color.og_blurple())
            history = await self.message.channel.history(limit=5).flatten()
            for message in history:
                msgembed.add_field(name=message.author.name, value=message.content, inline=False)
            embeds = [embed, msgembed]
            await webhook.send(embeds=embeds)
        except Exception as e:
            debug(e)


class Chat (discord.Cog) :
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
            message_to_redo=history[0]
        await ctx.respond("Message redone !", ephemeral=True)
        await mp.chat_process(self, message_to_redo)
    


    @discord.message_command(name="Downvote", description="Downvote a message")
    async def downvote(self, ctx: discord.ApplicationContext, message: discord.Message):
        modal = MyModal(message)
        await ctx.send_modal(modal)