import discord


def is_ignorable(content):
    if content.startswith("-") or content.startswith("//"):
        return True
    return False


async def fetch_messages_history(
    channel: discord.TextChannel, limit: int, original_message: discord.Message
) -> list[discord.Message]:
    messages = []
    if original_message == None:
        async for msg in channel.history(limit=100):
            if not is_ignorable(msg.content):
                messages.append(msg)
            if len(messages) == limit:
                break
    else:
        async for msg in channel.history(limit=100, before=original_message):
            if not is_ignorable(msg.content):
                messages.append(msg)
            if len(messages) == limit:
                break
    messages.reverse()
    return messages
