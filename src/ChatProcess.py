import asyncio
import os
import re
import discord
import datetime
import json

from src.utils.misc import moderate, ModerationError, Hasher
from src.utils.variousclasses import models, characters, apis
from src.guild import Guild
from src.chatUtils.Chat import fetch_messages_history
from src.utils.openaicaller import openai_caller
from src.functionscalls import (
    call_function,
    functions,
    server_normal_channel_functions,
    FuntionCallError,
)
from utils.misc import moderate, ModerationError


class Chat:
    def __init__(self, bot, message: discord.Message):
        self.bot = bot
        self.message: discord.Message = message
        self.guild = Guild(self.message.guild.id)
        self.author = message.author
        self.is_bots_thread = False

    async def getSupplementaryData(self) -> None:
        """
        This function gets various contextual data that will be needed later on
        - The original message (if the message is a reply to a previous message from the bot)
        - The channel the message was sent in (if the message was sent in a thread)
        """
        if isinstance(self.message.channel, discord.Thread):
            if self.message.channel.owner_id == self.bot.user.id:
                self.is_bots_thread = True
            self.channelIdForSettings = self.message.channel.parent_id
        else:
            self.channelIdForSettings = self.message.channel.id

        try:
            self.original_message = await self.message.channel.fetch_message(
                self.message.reference.message_id
            )
        except:
            self.original_message = None

        if (
            self.original_message != None
            and self.original_message.author.id == self.bot.user.id
        ):
            self.original_message = None

    async def preExitCriteria(self) -> bool:
        """
        Returns True if any of the exit criterias are met
        This checks if the guild has the needed settings for the bot to work
        """
        returnCriterias = []
        returnCriterias.append(self.message.author.id == self.bot.user.id)
        returnCriterias.append(self.api_key == None)
        returnCriterias.append(self.is_active == 0)
        return any(returnCriterias)

    async def postExitCriteria(self) -> bool:
        """
        Returns True if any of the exit criterias are met (their opposite is met but there is a not in front of the any() function)
        This checks if the bot should actuallly respond to the message or if the message doesn't concern the bot
        """
        returnCriterias = []
        returnCriterias.append(
            self.guild.sanitizedChannels.get(str(self.message.channel.id), None) != None
        )
        returnCriterias.append(
            self.message.content.find("<@" + str(self.bot.user.id) + ">") != -1
        )
        returnCriterias.append(self.original_message != None)
        returnCriterias.append(self.is_bots_thread)

        return not any(returnCriterias)

    async def getSettings(self):
        self.settings = self.guild.getChannelInfo(str(self.channelIdForSettings))
        self.model = self.settings["model"]
        self.character = self.settings["character"]
        self.openai_api_key = self.guild.api_keys.get("openai", None)
        if self.openai_api_key == None:
            raise Exception("No openai api key is set")

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
            if not moderate(self.openai_api_key, msg.content):
                self.context.append(
                    {
                        "role": role,
                        "content": msg.content,
                        "name": name,
                    }
                )
