import requests
import json
from os import path, environ
import subprocess
import whisper

python_path = environ["VIRTUAL_ENV"] + "/bin/python"  # PATH to venv python
recorder_path = "./record.py"

model = "mistral"
url = "http://localhost:11434/api/generate"
memory: list = []

with open("memory.txt", "r") as file:
    file_content = file.read()
    if path.getsize("memory.txt"):
        memory = list(map(int, file_content.split(",")))


recording_process = subprocess.Popen([python_path, recorder_path])


def get_answer(memory) -> str:
    question = input("Ask: ")

    data = {
        "model": f"{model}",
        "prompt": f"{question}",
        "stream": False,
        "context": memory,
    }

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
        memory = response.get("context")
        with open("memory.txt", "w") as file:
            file.write("")
            file.write(",".join(map(str, memory)))

    else:
        print("Request failed with status code:", response.status_code)

    return response.get("response")


try:
    recording_process.wait(20)

except KeyboardInterrupt:
    while True:
        get_answer(memory)

except subprocess.TimeoutExpired:
    print("Recording timed out")
