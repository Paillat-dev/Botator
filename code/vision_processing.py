import io
import os
import asyncio
from config import debug

# Imports the Google Cloud client library
from google.cloud import vision

# Instantiates a client
try:
    client = vision.ImageAnnotatorClient()
except:
    debug("Google Vision API is not setup, please run /setup")



async def process(attachment):
    try:
        debug("Processing image...")
        image = vision.Image()
        image.source.image_uri = attachment.url
        labels = client.label_detection(image=image)
        texts = client.text_detection(image=image)
        objects = client.object_localization(image=image)
        labels = labels.label_annotations
        texts = texts.text_annotations
        objects = objects.localized_object_annotations
        # we take the first 4 labels and the first 4 objects
        labels = labels[:2]
        objects = objects[:7]
        final = "<image\n"
        if len(labels) > 0:
            final += "Labels:\n"
        for label in labels:
            final += label.description + ", "
        final = final[:-2] + "\n"
        if len(texts) > 0:
            final += "Text:\n"
        try:
            final += (
                texts[0].description + "\n"
            )  # we take the first text, wich is the whole text in reality
        except:
            pass
        if len(objects) > 0:
            final += "Objects:\n"
        for obj in objects:
            final += obj.name + ", "
        final = final[:-2] + "\n"
        final += "!image>"
        # we store the result in a file called attachment.key.txt in the folder ./../database/google-vision/results
        # we create the folder if it doesn't exist
        if not os.path.exists("./../database/google-vision/results"):
            os.mkdir("./../database/google-vision/results")
        # we create the file
        with open(
            f"./../database/google-vision/results/{attachment.id}.txt",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(final)
            f.close()

        return final

    except Exception as e:
        debug("Error while processing image: " + str(e))
