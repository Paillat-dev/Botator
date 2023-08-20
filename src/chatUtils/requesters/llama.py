import os

from dotenv import load_dotenv
from src.utils.replicatepredictor import ReplicatePredictor

load_dotenv()

model_name = "replicate/llama-7b"
version_hash = "ac808388e2e9d8ed35a5bf2eaa7d83f0ad53f9e3df31a42e4eb0a0c3249b3165"
replicate_api_key = os.getenv("REPLICATE_API_KEY")


async def llama(prompt: str):
    predictor = ReplicatePredictor(replicate_api_key, model_name, version_hash)
    response = await predictor.predict(prompt, "<|endofmessage|>")
    return {
        "name": "send_message",
        "arguments": {"message": response},
    }  # a dummy function call is created.
