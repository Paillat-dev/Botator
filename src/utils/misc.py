from src.utils.openaicaller import openai_caller


async def moderate(api_key, text, recall_func=None):
    caller = openai_caller(api_key)
    response = await caller.moderation(
        recall_func,
        api_key=api_key,
        input=text,
    )
    return response["results"][0]["flagged"]  # type: ignore
