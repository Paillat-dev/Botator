import io
import os
import asyncio
# Imports the Google Cloud client library
from google.cloud import vision

#we set the env variable GOOGLE_APPLICATION_CREDENTIALS to the path of the json file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./../database/google-vision/botator-vision-8cd1030a7541.json"
# Instantiates a client
client = vision.ImageAnnotatorClient()






# The name of the image file to annotate
file_name = os.path.abspath('./../database/google-vision/label.jpg')
print(file_name)
# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
#response = client.label_detection(image=image)
#labels = response.label_annotations

#print('Labels:')
#for label in labels:
#    print(label.description)

async def get_labels(image):
    response = client.label_detection(image=image)
    labels = response.label_annotations
    return labels

async def get_text(image):
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts

#now we print the labels
async def main():
    labels = await get_labels(image)
    print('Labels:')
    for label in labels:
        print(label.description)
    texts = await get_text(image)
    print('Texts:')
    for text in texts:
        print(text.description)

#now we run the main function
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())