from googleapiclient import discovery
from config import perspective_api_key
import json
import re

client = discovery.build("commentanalyzer",
                            "v1alpha1",
                            developerKey=perspective_api_key,
                            discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                            static_discovery=False,
                        )

analyze_request = {
    'comment': {'text': ''},  # The text to analyze
    'requestedAttributes': {'TOXICITY': {}},  # Requested attributes
    #we will analyze the text in english, french & italian
    'languages': ['en', 'fr', 'it'],
    'doNotStore': 'true'  # We don't want google to store the data because of privacy reasons & the GDPR (General Data Protection Regulation, an EU law that protects the privacy of EU citizens and residents for data privacy and security purposes https://gdpr-info.eu/)
}   
def get_toxicity(message: str):
    #we first remove all kind of markdown from the message to avoid exploits
    message = re.sub(r'\*([^*]+)\*', r'\1', message)
    message = re.sub(r'\_([^_]+)\_', r'\1', message)
    message = re.sub(r'\*\*([^*]+)\*\*', r'\1', message)
    message = re.sub(r'\_\_([^_]+)\_\_', r'\1', message)
    message = re.sub(r'\|\|([^|]+)\|\|', r'\1', message)
    message = re.sub(r'\~([^~]+)\~', r'\1', message)
    message = re.sub(r'\~\~([^~]+)\~\~', r'\1', message)
    message = re.sub(r'\`([^`]+)\`', r'\1', message)
    message = re.sub(r'\`\`\`([^`]+)\`\`\`', r'\1', message) 
    analyze_request['comment']['text'] = message
    response = client.comments().analyze(body=analyze_request).execute()
    return float(response['attributeScores']['TOXICITY']['summaryScore']['value'])

#test part
def test():
    print(get_toxicity("Hello world"))
    print(get_toxicity("You are a stupid bot I hate you!!!"))
    print(get_toxicity("Je suis un bot stupide, je vous déteste !!!"))
    print(get_toxicity("Ciao, come state?"))
    print(get_toxicity("Siete tutti degli scemi"))
    print(get_toxicity("Siete tutti degli stupidi"))
    print(get_toxicity("Je n'aime pas les gens stupides"))
    #markdown removal test
    print(get_toxicity("You are all stupid"))
    print(get_toxicity("You are all *s*t*u*p*i*d"))
    print(print("*** you"))
#uncomment the following line to test the code
#test()