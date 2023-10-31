import datetime

from src.utils.variousclasses import models, characters, apis

promts = {}
for character in characters.reverseMatchingDict.keys():
    with open(
        f"src/chatUtils/prompts/{character}/chat.txt", "r", encoding="utf-8"
    ) as f:
        promts[character] = {}
        promts[character]["chat"] = f.read()

    with open(
        f"src/chatUtils/prompts/{character}/text.txt", "r", encoding="utf-8"
    ) as f:
        promts[character]["text"] = f.read()


def createPrompt(
    messages: list[dict],
    model: str,
    character: str,
    modeltype: str,
    guildName: str,
    channelName: str,
) -> str | list[dict]:
    """
    Creates a prompt from the messages list
    """
    if modeltype == "chat":
        prompt = createChatPrompt(messages, model, character)
        sysprompt = prompt[0]["content"]
        sysprompt = (
            sysprompt.replace("[server-name]", guildName)
            .replace("[channel-name]", channelName)
            .replace(
                "[date-and-time]",
                datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )
        prompt[0]["content"] = sysprompt
    elif modeltype == "text":
        prompt = (
            createTextPrompt(messages, model, character)
            .replace("[server-name]", guildName)
            .replace("[channel-name]", channelName)
            .replace(
                "[date-and-time]",
                datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
            )
        )
    else:
        raise ValueError("Invalid type")
    return prompt


def createTextPrompt(messages: list[dict], model: str, character: str) -> str:
    """
    Creates a text prompt from the messages list
    """
    global promts
    prompt = promts[character]["text"]
    for message in messages:
        if message["name"] == "assistant":
            message["name"] = character
        prompt += f"{message['name']}: {message['content']} <|endofmessage|>\n"
    prompt += f"{character}:"
    return prompt


def createChatPrompt(messages: list[dict], model: str, character: str) -> str:
    """
    Creates a chat prompt from the messages list
    """
    global promts
    prompt = promts[character]["chat"]
    final_prompt = [{"role": "system", "content": prompt}]
    final_prompt.extend(messages)
    return final_prompt
