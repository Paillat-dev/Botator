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

chat_models = ["gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
text_models = ["text-davinci-003", "text-davinci-002", "text-curie-001", "text-babbage-001", "text-ada-001"]

models_max_tokens = {
    "gpt-4": 8_192,
    "gpt-4-32k": 32_768,
    "gpt-3.5-turbo": 4_096,
    "gpt-3.5-turbo-16k": 16_384,
    "text-davinci-003": 4_097,
    "text-davinci-002": 4_097,
    "text-curie-001": 2_049,
    "text-babbage-001": 2_049,
    "text-ada-001": 2_049,
}

class openai_caller:
    def __init__(self, api_key=None) -> None:
        pass
    def set_api_key(self, key):
        openai_module.api_key = key
    async def generate_response(self, **kwargs):
        if kwargs['model'] in chat_models:
            return await self.chat_generate(**kwargs)
        elif kwargs['model'] in text_models:
            raise NotImplementedError("Text models are not supported yet")
        else:
            raise ValueError("Model not found")
    async def chat_generate(self, **kwargs):
        tokens = await num_tokens_from_messages(kwargs['messages'], kwargs['model'])
        model_max_tokens = models_max_tokens[kwargs['model']]
        while tokens > model_max_tokens:
            kwargs['messages'] = kwargs['messages'][1:]
            print(f"{bcolors.BOLD}{bcolors.WARNING}Warning: Too many tokens. Removing first message.{bcolors.ENDC}")
            tokens = await num_tokens_from_messages(kwargs['messages'], kwargs['model'])
        i = 0
        response = None
        while i < 10:
            try:
                response = await openai_module.ChatCompletion.acreate(**kwargs)
                break
            except APIError:
                await asyncio.sleep(10)
                i += 1
            except Timeout:
                await asyncio.sleep(10)
                i += 1
            except RateLimitError:
                await asyncio.sleep(10)
                i += 1
            except APIConnectionError as e:
                print(e)
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}APIConnectionError. There is an issue with your internet connection. Please check your connection.{bcolors.ENDC}")
                raise e
            except InvalidRequestError as e:
                print(e)
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}InvalidRequestError. Please check your request.{bcolors.ENDC}")
                raise e
            except AuthenticationError as e:
                print(e)
                print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}AuthenticationError. Please check your API key.{bcolors.ENDC}")
                raise e
            except ServiceUnavailableError:
                await asyncio.sleep(10)
                i += 1
            finally:
                if i == 10:
                    print(f"\n\n{bcolors.BOLD}{bcolors.FAIL}OpenAI API is not responding. Please try again later.{bcolors.ENDC}")
                    raise TimeoutError("OpenAI API is not responding. Please try again later.")
        return response # type: ignore