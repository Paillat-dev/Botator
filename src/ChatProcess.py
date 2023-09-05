import asyncio
import os
import re
import discord
import datetime
import json

from src.utils.misc import moderate
from src.utils.variousclasses import models, characters
from src.guild import Guild
from src.chatUtils.Chat import fetch_messages_history, is_ignorable
from src.chatUtils.prompts import createPrompt
from src.functionscalls import call_function, server_normal_channel_functions, functions
from src.chatUtils.requesters.request import request


class Chat:
    def __init__(self, bot: discord.bot, message: discord.Message):
        self.bot = bot
        self.message: discord.Message = message
        self.guild = Guild(self.message.guild.id)
        self.author = message.author
        self.is_bots_thread = False
        self.depth = 0

    async def getSupplementaryData(self) -> None:
        """
        This function gets various contextual data that will be needed later on
        - The original message (if the message is a reply to a previous message from the bot)
        - The channel the message was sent in (if the message was sent in a thread)
        """
        if isinstance(self.message.channel, discord.Thread):
            if self.message.channel.owner_id == self.bot.user.id:
                self.is_bots_thread = True
            self.channelIdForSettings = str(self.message.channel.parent_id)
        else:
            self.channelIdForSettings = str(self.message.channel.id)

        try:
            self.original_message = await self.message.channel.fetch_message(
                self.message.reference.message_id
            )
        except:
            self.original_message = None

        if (
            self.original_message != None
            and self.original_message.author.id != self.bot.user.id
        ):
            self.original_message = None

    async def preExitCriteria(self) -> bool:
        """
        Returns True if any of the exit criterias are met
        This checks if the guild has the needed settings for the bot to work
        """
        returnCriterias = []
        returnCriterias.append(self.message.author.id == self.bot.user.id)
        returnCriterias.append(is_ignorable(self.message.content))
        return any(returnCriterias)

    async def postExitCriteria(self) -> bool:
        """
        Returns True if any of the exit criterias are met (their opposite is met but there is a not in front of the any() function)
        This checks if the bot should actuallly respond to the message or if the message doesn't concern the bot
        """

        serverwideReturnCriterias = []
        serverwideReturnCriterias.append(self.original_message != None)
        serverwideReturnCriterias.append(
            self.message.content.find(f"<@{self.bot.user.id}>") != -1
        )
        serverwideReturnCriterias.append(self.is_bots_thread)

        channelReturnCriterias = []
        channelReturnCriterias.append(self.channelIdForSettings != "serverwide")
        channelReturnCriterias.append(
            self.guild.getChannelInfo(self.channelIdForSettings) != None
        )

        messageReturnCriterias = []
        messageReturnCriterias.append(
            any(serverwideReturnCriterias)
            and self.guild.getChannelInfo("serverwide") != None
        )
        messageReturnCriterias.append(all(channelReturnCriterias))

        returnCriterias: bool = not any(messageReturnCriterias)
        return returnCriterias

    async def getSettings(self):
        self.settings = self.guild.getChannelInfo(
            str(self.channelIdForSettings)
        ) or self.guild.getChannelInfo("serverwide")
        if self.settings == None:
            return True
        self.model = self.settings["model"]
        self.character = self.settings["character"]
        self.openai_api_key = self.guild.api_keys.get("openai", None)
        if self.openai_api_key == None:
            raise Exception("No openai api key is set")
        self.type = "chat" if self.model in models.chatModels else "text"

    async def formatContext(self):
        """
        This function formats the context for the bot to use
        """
        messages: list[discord.Message] = await fetch_messages_history(
            self.message.channel, 10, self.original_message
        )
        self.context = []
        for msg in messages:
            if msg.author.id == self.bot.user.id:
                role = "assistant"
                name = "assistant"
            else:
                role = "user"
                name = msg.author.global_name
                # use re not make name match ^[a-zA-Z0-9_-]{1,64}$ by removing all non-alphanumeric characters
                name = re.sub(r"[^a-zA-Z0-9_-]", "", name, flags=re.UNICODE)
                if name == "":
                    name = msg.author.name
            if not await moderate(self.openai_api_key, msg.content):
                self.context.append(
                    {
                        "role": role,
                        "content": msg.content,
                        "name": name,
                    }
                )
            else:
                try:
                    await msg.add_reaction("🤬")
                except:
                    pass

    async def createThePrompt(self):
        self.prompt = createPrompt(
            messages=self.context,
            model=self.model,
            character=self.character,
            modeltype=self.type,
            guildName=self.message.guild.name,
            channelName=self.message.channel.name,
        )

    async def getResponse(self):
        """
        This function gets the response from the ai
        """
        funcs = functions.copy()
        if isinstance(self.message.channel, discord.TextChannel):
            funcs.extend(server_normal_channel_functions)
        self.response = await request(
            model=self.model,
            prompt=self.prompt,
            openai_api_key=self.openai_api_key,
            funtcions=funcs,
            custom_temp=characters.custom_temp.get(self.character, 1.2),
        )

    async def processResponse(self):
        response = await call_function(
            message=self.message,
            function_call=self.response,
            api_key=self.openai_api_key,
        )
        if response[0] != None:
            await self.processFunctioncallResponse(response)

    async def processFunctioncallResponse(self, response):
        self.context.append(
            {
                "role": "function",
                "content": response[0],
                "name": response[1],
            }
        )
        if self.depth < 3:
            await self.createThePrompt()
            await self.getResponse()
            await self.processResponse()
        else:
            await self.message.channel.send(
                "It looks like I'm stuck in a loop. Sorry about that."
            )

    async def process(self):
        """
        This function processes the message
        """
        if await self.preExitCriteria():
            return
        await self.getSupplementaryData()
        if await self.getSettings():
            return
        if await self.postExitCriteria():
            return
        try:
            await self.message.channel.trigger_typing()
            await self.message.add_reaction("🤔")
            await self.formatContext()
            await self.createThePrompt()
            await self.getResponse()
            await self.processResponse()
            await self.message.remove_reaction("🤔", self.message.guild.me)
        except Exception as e:
            try:
                self.message.remove_reaction("🤔", self.message.guild.me)
            except:
                pass
            if isinstance(e, TimeoutError):
                await self.message.channel.send(
                    "Due to OpenAI not doing their work, I can unfortunately not answer right now. Do retry soon!",
                    delete_after=5,
                )
            else:
                await self.message.channel.send(
                    f"""An error occured while processing your message, we are sorry about that. Please check your settings and try again later. If the issue persists, please join uor discord server here: https://discord.gg/pB6hXtUeDv and send the following logs:
```
{e}
```""",
                    delete_after=4,
                )
            try:
                await self.message.add_reaction("😞")
            except:
                pass
            raise e
