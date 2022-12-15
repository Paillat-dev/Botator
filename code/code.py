#coucou c'est fives
# wesh wesh ici latouff
import discord # pip install pycord
import asyncio # pip install asyncio
import cogs # import the cogs
import datetime # pip install datetime
from config import debug, connp, cp # import the debug function and the database connection
import apsw # pip install apsw. ApSW is a Python interface to SQLite 3
bot = discord.Bot(intents=discord.Intents.all(), help_command=None)

bot.add_cog(cogs.Setup(bot))
bot.add_cog(cogs.Settings(bot))
bot.add_cog(cogs.Help(bot))
bot.add_cog(cogs.Chat(bot))
bot.add_cog(cogs.ManageChat(bot))

'''
def reset_uses_count_today():
    c.execute("UPDATE data SET uses_count_today = 0")
    conn.commit()
#get the current date and save it in the previous_date variable
#if the day number is different from the previous day number, reset the uses count today
def check_day():
    global previous_date
    if datetime.datetime.now().day != previous_date.day:
        previous_date = datetime.datetime.now()
        previous_date = datetime.datetime.now()
        return True
    else:
        previous_date = datetime.datetime.now()
        return False
#run check_day every 10 seconds
async def check_day_task():
    while True:
        check_day()
        await asyncio.sleep(60)
#add a task to the bot that runs check_day every 1 minute
bot.loop.create_task(check_day_task())
'''


#run the bot
# Replace the following with your bot's token
with open("./key.txt") as f:
    key = f.read()
   
bot.run(key)