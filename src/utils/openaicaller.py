"""
This file provides a Python module that wraps the OpenAI API for making API calls.

The module includes:

- Functions for generating responses using chat-based models and handling API errors.
- Constants for chat and text models and their maximum token limits.
- Imports for required modules, including OpenAI and asyncio.
- A color formatting class, `bcolors`, for console output.

The main component is the `openai_caller` class with methods:
- `__init__(self, api_key=None)`: Initializes an instance of the class and sets the API key if provided.
- `set_api_key(self, key)`: Sets the API key for OpenAI.
- `generate_response(self, **kwargs)`: Asynchronously generates a response based on the provided arguments.
- `chat_generate(self, **kwargs)`: Asynchronously generates a chat-based response, handling token limits and API errors.

The module assumes the presence of `num_tokens_from_messages` function in a separate module called `utils.tokens`, used for token calculation.

Refer to function and method documentation for further details.
"""


import openai as openai_module
import asyncio

from openai.error import APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError, AuthenticationError, ServiceUnavailableError
from src.utils.tokens import num_tokens_from_messages

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

chat_models = ["gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613"]
text_models = ["text-davinci-003", "text-davinci-002", "text-curie-001", "text-babbage-001", "text-ada-001"]

models_max_tokens = {
    "gpt-4": 8_192,
    "gpt-4-32k": 32_768,
    "gpt-3.5-turbo": 4_096,
    "gpt-3.5-turbo-0613": 4_096,
    "gpt-3.5-turbo-16k": 16_384,
    "text-davinci-003": 4_097,
    "text-davinci-002": 4_097,
    "text-curie-001": 2_049,
    "text-babbage-001": 2_049,
    "text-ada-001": 2_049,
}

class openai_caller:
    def __init__(self, api_key=None) -> None:
        self.api_key = api_key
    async def generate_response(self, error_call=None, **kwargs):
        if error_call is None:
            error_call = lambda x: 2 # do nothing
        if kwargs.get("model", "") in chat_models:
            return await self.chat_generate(error_call, **kwargs)
        elif kwargs.get("engine", "") in text_models:
            raise NotImplementedError("Text models are not supported yet")
        else:
            raise ValueError("Model not found")
    async def chat_generate(self, recall_func, **kwargs):
        tokens = await num_tokens_from_messages(kwargs['messages'], kwargs['model'])
        model_max_tokens = models_max_tokens[kwargs['model']]
        while tokens > model_max_tokens:
            kwargs['messages'] = kwargs['messages'][1:]
            print(f"{bcolors.BOLD}{bcolors.WARNING}Warning: Too many tokens. Removing first message.{bcolors.ENDC}")
            tokens = await num_tokens_from_messages(kwargs['messages'], kwargs['model'])
        i = 0
        response = None
        kwargs['api_key'] = self.api_key
        while i < 10:
            try:
                response = await openai_module.ChatCompletion.acreate(
                    **kwargs
                    )
                break
            except APIError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.WARNING}APIError. This is not your fault. Retrying...{bcolors.ENDC}")
                await recall_func("`An APIError occurred. This is not your fault. Retrying...`")
                await asyncio.sleep(10)
                await recall_func()
                i += 1
            except Timeout as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.WARNING}The request timed out. Retrying...{bcolors.ENDC}")
                await recall_func("`The request timed out. Retrying...`")
                await asyncio.sleep(10)
                await recall_func()
                i += 1
            except RateLimitError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.WARNING}RateLimitError. You are being rate limited. Retrying...{bcolors.ENDC}")
                await recall_func("`You are being rate limited. Retrying...`")
                await asyncio.sleep(10)
                await recall_func()
                i += 1
            except APIConnectionError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}APIConnectionError. There is an issue with your internet connection. Please check your connection.{bcolors.ENDC}")
                await recall_func()
                raise e
            except InvalidRequestError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}InvalidRequestError. Please check your request.{bcolors.ENDC}")
                await recall_func()
                raise e
            except AuthenticationError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}AuthenticationError. Please check your API key and if needed, also your organization ID.{bcolors.ENDC}")
                await recall_func("`AuthenticationError. Please check your API key.`")
                raise e
            except ServiceUnavailableError as e:
                print(f"\n\n{bcolors.BOLD}{bcolors.WARNING}ServiceUnavailableError. The OpenAI API is not responding. Retrying...{bcolors.ENDC}")
                await recall_func("`The OpenAI API is not responding. Retrying...`")
                await asyncio.sleep(10)
                await recall_func()
                i += 1
            finally:
                if i == 10:
                    print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}OpenAI API is not responding. Please try again later.{bcolors.ENDC}")
                    raise TimeoutError("OpenAI API is not responding. Please try again later.")
        return response # type: ignore
    
##testing
if __name__ == "__main__":
    async def main():
        openai = openai_caller(api_key="sk-")
        response = await openai.generate_response(
            model="gpt-3.5-turbo",
            messages=[{"role":"user", "content":"ping"}],
            max_tokens=5,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n", " Human:", " AI:"]
        )
        print(response)
    asyncio.run(main())