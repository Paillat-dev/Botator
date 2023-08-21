import discord


class Help(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.slash_command(name="help", description="Show all the commands")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Help",
            description="Here is the help page",
            color=discord.Color.dark_teal(),
        )
        # we will iterate over all commands the bot has and add them to the embed
        for command in self.bot.commands:
            fieldname = command.name
            fielddescription = command.description
            embed.add_field(name=fieldname, value=fielddescription, inline=False)
        embed.set_footer(text="Made with ❤️ by paillat : https://paillat.dev")
        await ctx.respond(embed=embed, ephemeral=True)
