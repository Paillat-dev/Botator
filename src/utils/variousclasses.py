from discord import AutocompleteContext


class models:
    matchingDict = {
        "chatGPT (default - free)": "gpt-3.5-turbo",
        "davinci (premium)": "text-davinci-003",
        "llama (premium)": "text-llama",
        "llama 2 (premium)": "text-llama-2",
    }
    reverseMatchingDict = {v: k for k, v in matchingDict.items()}
    default = list(matchingDict.keys())[0]
    openaimodels = ["gpt-3.5-turbo", "text-davinci-003"]
    chatModels = ["gpt-3.5-turbo"]

    @classmethod
    async def autocomplete(cls, ctx: AutocompleteContext) -> list[str]:
        modls = cls.matchingDict.keys()
        return [model for model in modls if model.find(ctx.value.lower()) != -1]


class characters:
    matchingDict = {
        "Botator (default - free)": "botator",
        "Quantum (premium)": "quantum",
    }
    reverseMatchingDict = {v: k for k, v in matchingDict.items()}
    default = list(matchingDict.keys())[0]

    @classmethod
    async def autocomplete(cls, ctx: AutocompleteContext) -> list[str]:
        chars = characters = cls.matchingDict.keys()
        return [
            character for character in chars if character.find(ctx.value.lower()) != -1
        ]


class apis:
    matchingDict = {
        "OpenAI": "openai",
    }

    @classmethod
    async def autocomplete(cls, ctx: AutocompleteContext) -> list[str]:
        apiss = cls.matchingDict.keys()
        return [api for api in apiss if api.find(ctx.value.lower()) != -1]
