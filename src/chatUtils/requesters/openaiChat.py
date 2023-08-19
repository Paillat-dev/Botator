from src.utils.openaicaller import openai_caller


async def openaiChat(messages, function):
    caller = openai_caller()
