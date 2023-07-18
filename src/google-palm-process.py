import requests

proxy_url = "http://64.225.4.12:9991"  # Replace with your actual proxy URL and port

api_key = "S"
model_name = "chat-bison-001"
api_url = f"https://autopush-generativelanguage.sandbox.googleapis.com/v1beta2/models/{model_name}:generateMessage?key={api_key}"

headers = {"Content-Type": "application/json"}

data = {
    "prompt": {"messages": [{"content": "hi"}]},
    "temperature": 0.1,
    "candidateCount": 1,
}

proxies = {"http": proxy_url, "https": proxy_url}

response = requests.post(api_url, headers=headers, json=data, proxies=proxies)

if response.status_code == 200:
    result = response.json()
    print(result)
else:
    print(f"Request failed with status code {response.status_code}")
