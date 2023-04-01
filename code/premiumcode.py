import discord # pip install pycord
import asyncio # pip install asyncio
import sqlite3 # pip install sqlite3
import logging # pip install logging
import os # pip install os
intents = discord.Intents.all()
conn = sqlite3.connect('../database/premium.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data (user_id text, guild_id text, premium boolean)''')
conn.commit()
bot = discord.Bot()
logging.basicConfig(level=logging.INFO)
@bot.command()
@discord.commands.option(name="server id", description="The server id for which you want to activate premium features", required=True)
async def activate_premium(ctx, server_id):
    #first check if the user is already in the database, select guuild_id and premium from the data table where user_id is the author's id
    logging.info("Activating premium for user " + str(ctx.author.id))
    c.execute("SELECT guild_id, premium FROM data WHERE user_id = ?", (ctx.author.id,))
    #if a guild_id is found, override the old settings with the new ones
    if c.fetchone() is not None:
        c.execute("UPDATE data SET guild_id = ?, premium = ? WHERE user_id = ?", (server_id, True, ctx.author.id))
        conn.commit()
        logging.info("Premium activated for server " + server_id + "by user " + str(ctx.author.id))
        await ctx.respond("Premium activated for server " + server_id, ephemeral=True)
    #if no guild_id is found, insert the new settings
    else:
        c.execute("INSERT INTO data VALUES (?, ?, ?)", (ctx.author.id, server_id, True))
        conn.commit()
        logging.info("Premium updated for server " + server_id + "by user " + str(ctx.author.id))
        await ctx.respond("Premium activated for server " + server_id, ephemeral=True)

#each 24 hours, check if each user if they have the premium role "1050823446445178900" in the server "1050769643180146749"
async def check_premium():
    while True:
        #select user_id and guild_id from the data table
        c.execute("SELECT user_id, guild_id FROM data")
        for row in c.fetchall():
            #get the guild and the user
            guild = bot.get_guild(int(row[1]))
            user = guild.get_member(int(row[0]))
            #if the user has the premium role, set premium to true
            logging.info("Checking premium for user " + str(row[0]))
            if discord.utils.get(user.roles, id=1050823446445178900) is not None:
                c.execute("UPDATE data SET premium = ? WHERE user_id = ?", (True, row[0]))
                conn.commit()
                logging.info("Premium activated for server " + str(row[1]) + "by user " + str(row[0]))
            #if the user does not have the premium role, set premium to false
            else:
                c.execute("UPDATE data SET premium = ? WHERE user_id = ?", (False, row[0]))
                conn.commit()
                logging.info("Premium deactivated for server " + str(row[1]) + "by user " + str(row[0]))
        await asyncio.sleep(86400)

#add a task to the bot that runs check_premium every 24 hours
bot.loop.create_task(check_premium())
#run the bot
# Replace the following with your bot's token
with open("./premium-key.txt") as f:
    key = f.read()
bot.run(key)