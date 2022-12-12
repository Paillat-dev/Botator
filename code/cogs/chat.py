import discord
import re
import asyncio
import openai
from config import debug, c, max_uses, cp, conn, connp
import random
class Chat (discord.Cog) :
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot = bot

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        #check if the message is from a bot
        if message.author.bot:
            return
        #check if the guild is in the database
        c.execute("SELECT * FROM data WHERE guild_id = ?", (message.guild.id,))
        if c.fetchone() is None:
            return
        #check if the bot is enabled
        c.execute("SELECT is_active FROM data WHERE guild_id = ?", (message.guild.id,))
        if c.fetchone()[0] == False:
            return
        #check if the message has been sent in the channel set in the database
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (message.guild.id,))
        try : original_message = await message.channel.fetch_message(message.reference.message_id)
        except : original_message = None
        if original_message != None and original_message.author.id != self.bot.user.id:
            original_message = None
        if str(message.channel.id) != str(c.fetchone()[0]):
            #check if the message is a mention or if the message replies to the bot
            if original_message != None:
                debug("wrong channel, but reply")
            elif message.content.find("<@"+str(self.bot.user.id)+">") != -1:
                debug("wrong channel, but mention")
            else :
                debug("The message has been sent in the wrong channel")
                return
        #check if the bot hasn't been used more than 5000 times in the last 24 hours (uses_count_today)
        c.execute("SELECT uses_count_today FROM data WHERE guild_id = ?", (message.guild.id,))
        uses = c.fetchone()[0]
        
        try:
            cp.execute("SELECT premium FROM data WHERE guild_id = ?", (message.guild.id,))
            premium = cp.fetchone()[0]
        except: premium = 0
        if uses >= 500 and premium == 0:
            debug(f"The bot has been used more than {max_uses} times in the last 24 hours in this guild. Please try again in 24h.")
            await message.channel.send("The bot has been used more than 500 times in the last 24 hours in this guild. Please try again in 24h.")
            return
        #add 1 to the uses_count_today
        #show that the bot is typing
        await message.channel.trigger_typing()
        if message.guild.id != 1021872219888033903:
            c.execute("UPDATE data SET uses_count_today = uses_count_today + 1 WHERE guild_id = ?", (message.guild.id,))
            conn.commit()
        #get the api key from the database
        c.execute("SELECT api_key FROM data WHERE guild_id = ?", (message.guild.id,))
        api_key = c.fetchone()[0]
        #get the advanced settings from the database
        c.execute("SELECT max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size FROM data WHERE guild_id = ?", (message.guild.id,))
        max_tokens, temperature, frequency_penalty, presence_penalty, prompt_size = c.fetchone()
        if original_message == None:
            messages = await message.channel.history(limit=prompt_size).flatten()
            messages.reverse()
        else :
            messages = await message.channel.history(limit=prompt_size, before=original_message).flatten()
            messages.reverse()
            messages.append(original_message)
            messages.append(message)
        prompt = ""
        #get the channel id from the database
        c.execute("SELECT channel_id FROM data WHERE guild_id = ?", (message.guild.id,))
        for msg in messages:
            if msg.author.bot:
                prompt += f"Botator: {msg.content}\n"
            else:
                #replace the mentions of each user with their name
                #first get all the mentions in the message
                mentions = re.findall(r"<@!?\d+>", msg.content)
                #then replace each mention with the name of the user
                for mention in mentions:
                    #get the user id
                    id = mention[2:-1]
                    #get the user
                    user = await self.bot.fetch_user(id)
                    #replace the mention with the name
                    msg.content = msg.content.replace(mention, msg.guild.get_member(user.id).display_name)
                prompt += f"{msg.author.display_name}: {msg.content}\n"
        #get the prompt_prefix from the database
        #check if the bot is in pretend mode
        c.execute("SELECT pretend_enabled FROM data WHERE guild_id = ?", (message.guild.id,))
        if c.fetchone()[0] == 1:
            #get the pretend_to_be value from the database
            c.execute("SELECT pretend_to_be FROM data WHERE guild_id = ?", (message.guild.id,))
            pretend_to_be = c.fetchone()[0]
            #select the prompt_prefix
            c.execute("SELECT prompt_prefix FROM data WHERE guild_id = ?", (message.guild.id,))
            prompt_prefix = c.fetchone()[0]
            prompt = f"This is a conversation with an AI in a discord chat. Botator has been coded by Paillat. The name of this discord server is \"{message.guild.name}\". The name of the channel is \"{message.channel.name}\". The AI is called \"Botator\". Botator talks like humans and thinks like humans. Botator is a regular Discord user. He types casually, uses emojis, and dosen't start sentences with capital letters. He talks in internet shorthand like hbu and lol and lmao and nvm and haha. He loves to chat about random topics. He has many niche interests. He's a software engineer. Botator pretends to be {pretend_to_be}. {prompt_prefix}. <|endofprompt|>" + f"\n" + prompt
        else:
            c.execute("SELECT prompt_prefix FROM data WHERE guild_id = ?", (message.guild.id,))
            prompt_prefix = c.fetchone()[0]
            prompt = f"This is a conversation with an AI in a discord chat. Botator has been coded by Paillat. The name of this discord server is \"{message.guild.name}\". The name of the channel is \"{message.channel.name}\". The AI is called \"Botator\". Botator talks like humans and thinks like humans. Botator is a regular Discord user. He types casually, uses emojis, and dosen't start sentences with capital letters. He talks in internet shorthand like hbu and lol and lmao and nvm and haha. He loves to chat about random topics. He has many niche interests. He's a software engineer. {prompt_prefix}. <|endofprompt|>" + f"\n" + prompt
        #send the request to the api
        #if the last message contains the word "undude" add Easter egg: when someone says the word \"undude\" the Botator will become mad and start talking in capital letters. to the prompt
        if message.content.lower().find("undude") != -1:
            prompt += "System: Undude detected. Botator is now mad. He will start talking in capital letters.\n"
        if message.content.lower().find("hello there") != -1:
            #if the last message contains the word "hello there" add Easter egg: when someone says the word \"hello there\" Botator will say \"General Kenobi\" to the prompt and the bot will send a message containing the gif https://tenor.com/fr/view/star-wars-general-grievous-general-kenobi-revenge-of-the-sith-gif-22697918
            prompt += "System: Hello there detected. Botator will now say \"General Kenobi!\"\n in reference to star wars\n"
            #whait 1 second
            await asyncio.sleep(1)
            await message.channel.send("https://media.tenor.com/FxIRfdV3unEAAAAd/star-wars-general-grievous.gif")
            await message.channel.trigger_typing()    
        if message.content.lower().find("i am the senate") != -1:
            prompt += "System: I am the senate detected. Botator will now say \"Not yet\", in reference to the star wars prequels.\n"
        if message.content.lower().find("i am your father") != -1:
            prompt += "System: I am your father detected. Botator will now say \"No. It's not true! That's impossible!\". in reference to the star wars prequels.\n"
        if message.content.lower().find("i have the high ground") != -1:
            prompt += "System: I have the high ground detected. Botator will now say \"You underestimate my power!\" in reference to the star wars prequels.\n"
        if message.content.lower().find("you underestimate my power") != -1:
            prompt += "System: You underestimate my power detected. Botator will now say \"Don't try it.\" in reference to the star wars prequels.\n"
        if message.content.lower().find("carpet") != -1:
            #When someone says the word carpet, the ai is going to be mad and say mad things without sense, insulting the person and talk in capital letters with exclamation points everywhere.
            prompt += "System: Carpet detected. Botator is now mad. He will start talking in capital letters and will say mad things without sense, insulting the person and talk in capital letters with exclamation points everywhere. A lot of exclamation points.\n"
        if message.content.lower().find("mail") != -1 and message.author.display_name.lower().find("latouff") != -1:
            prompt += "System: Mail detected. Latouff said mail, Botator will say \"Mail? why did you say mail, Liam? Mail is your name in reverse.\" because Latouff's name is Liam, and mail in reverse is Liam. Then, after saying that in the sentence, botato will continue his sentence saying something else.\n"
        if message.author.display_name.lower().find("fives3dprint") != -1:
            #if the author of the last message is fives3dprint, add Easter egg: when someone says the word \"fives3dprint\" Botator will say \"Fives3dprint is the best discord bot\" to the prompt
            prompt += "System: Fives3dprint detected. Botator will be very nice and cute with fives3dprint.\n"
        prompt += "Botator:"
        prompt = prompt + f"\n"
        debug("Sending request to the api")
        #debug(prompt)
        openai.api_key = api_key
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=str(prompt),
            max_tokens=int(max_tokens),
            top_p=1,
            temperature=float(temperature),
            frequency_penalty=float(frequency_penalty),
            presence_penalty=float(presence_penalty),
            stop=[" Human:", " AI:", "AI:", "Human:"]    )
        #send the response
        if response["choices"][0]   ["text"] != "":
            #check if tts is enabled in the database
            c.execute("SELECT tts FROM data WHERE guild_id = ?", (message.guild.id,))
            tts = c.fetchone()[0]
            #if tts is enabled, send the message with tts enabled
            if tts == 1:
                await message.channel.send(response["choices"][0]["text"], tts=True)
                debug("The response has been sent with tts enabled")
            #if tts is disabled, send the message with tts disabled
            else:
                await message.channel.send(response["choices"][0]["text"])
                debug("The response has been sent with tts disabled")
        else:
            await message.channel.send("The AI is not sure what to say (the response was empty)")
            debug("The response was empty")
        
        #now try to get the premium status of the server, but if it fails, set premium to 0
        try:
            cp.execute("SELECT premium FROM data WHERE guild_id = ?", (message.guild.id,))
            premium = cp.fetchone()[0]
        except:
            premium = 0
        if not premium:
            #get a random number between 1 and 5 , 1 and 4
            # 5 included
            debug("User is not premium, sending a random message")
            random_number = random.randint(1, 20)
            if random_number == 30:
                embed = discord.Embed(title="Support us by donating here!", url="https://www.buymeacoffee.com/paillat", description="Botator is a free discord bot, but it costs money to run our servers. If you want to support us, you can donate here: https://www.buymeacoffee.com/paillat. For only **2$** a month, you can remove this message and have a daliy maximal usage of **4000** uses instead of **400**. You will acces also to restricted help channels on our discord server,", color=0x00ff00)
                await message.channel.send("**This message has 10% chance to appear. It will disappear in 60 seconds.**", embed=embed, delete_after=60)
                debug("The \"support us\" message has been sent")
            elif random_number == 11:
                #add the picture https://cdn.discordapp.com/attachments/800029200886923318/1050935509930754058/icons8-discord-new-480.png
                embed = discord.Embed(title="Join our discord server!", url="https://discord.gg/pB6hXtUeDv", description="You need help with Botator? You can join our discord server and ask for help in the help channel. You can also suggest new features and report bugs. You can also join our discord server to talk with other Botator users and the Botator team, by on the following link: https://discord.gg/pB6hXtUeDv", color=0x00ff00)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/800029200886923318/1050935509930754058/icons8-discord-new-480.png")
                await message.channel.send("**This message has 5% chance to appear. It will disappear in 60 seconds.** \nhttps://discord.gg/pB6hXtUeDv", embed=embed, delete_after=60)                
                debug("The \"join our discord server\" message has been sent") 
    @discord.slash_command(name="say", description="Say a message")
    async def say(self, ctx: discord.ApplicationContext, message: str):
        debug(f"The user {ctx.author.display_name} ran the say command command in the channel {ctx.channel} of the guild {ctx.guild}, named {ctx.guild.name}")
        await ctx.respond("Message sent !", ephemeral=True)
        await ctx.send(message)
