import orjson
from src.utils.openaicaller import openai_caller


async def openaiChat(
    messages, functions, openai_api_key, model="gpt-3.5-turbo", temperature=1.2
):
    caller = openai_caller()
    response = await caller.generate_response(
        api_key=openai_api_key,
        model=model,
        temperature=temperature,
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response = response["choices"][0]["message"]  # type: ignore
    if response.get("function_call", False):
        function_call = response["function_call"]
        return {
            "name": function_call["name"],
            "arguments": orjson.loads(function_call["arguments"]),
        }
    else:
        return {
            "name": "send_message",
            "arguments": {"message": response["content"]},
        }
