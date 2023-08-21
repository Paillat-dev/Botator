import replicate
import asyncio


class ReplicatePredictor:
    def __init__(self, api_key, model_name, version_hash):
        self.api_key = api_key
        self.model_name = model_name
        self.version_hash = version_hash
        self.client = replicate.Client(api_token=self.api_key)
        self.model = self.client.models.get(self.model_name)
        self.version = self.model.versions.get(self.version_hash)

    def prediction_thread(self, prompt, stop=None):
        output = self.client.predictions.create(
            version=self.version,
            input={"prompt": prompt},
        )
        finaloutput = ""
        for out in output.output_iterator():
            finaloutput += out
            if stop != None and finaloutput.find(stop) != -1:
                output.cancel()
        if stop != None:
            return finaloutput.split(stop)[0]
        else:
            return finaloutput

    async def predict(self, prompt, stop=None):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, lambda: self.prediction_thread(prompt, stop)
        )
        return result
