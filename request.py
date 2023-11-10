import requests
import json

model = "mistral"
question = "How are you?"

url = "http://localhost:11434/api/generate"

data = {"model": f"{model}", "prompt": f"{question}", "stream": False}

# Convert the data to JSON format
payload = json.dumps(data)

# Set the headers for the POST request
headers = {"Content-Type": "application/json"}

# Make the POST request
response = requests.post(url, data=payload, headers=headers)


# Check the response status code and content
if response.status_code == 200:
    print("Request successful")

    # Convert JSON to dictionary
    response = response.json()

    # print(response.text)
    print("Response:")
    print(response.get("response"))
    print(response.get("total_duration") / 10**9)
else:
    print("Request failed with status code:", response.status_code)
