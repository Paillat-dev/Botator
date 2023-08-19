import discord
from src.chatUtils.requesters.openaiChat import openaiChat
from src.chatUtils.requesters.openaiText import openaiText
from src.chatUtils.requesters.llama import llama
from src.chatUtils.requesters.llama2 import llama2


async def request(
    model: str, prompt: list[dict] | str, message: discord.message, openai_api_key: str
):
    if model == "gpt-3.5-turbo":
        return await openaiChat(messages=prompt, openai_api_key=openai_api_key)
    elif model == "text-davinci-003":
        return await openaiText(prompt=prompt, openai_api_key=openai_api_key)
    elif model == "text-llama":
        return await llama(prompt=prompt)
    elif model == "text-llama-2":
        return await llama2(prompt=prompt)
