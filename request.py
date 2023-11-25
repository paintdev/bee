import time
import requests
import json
from os import path, environ, listdir, remove

import subprocess
import whisper
import re


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
    name_pattern = re.compile(r"recording_*")
    for file_name in listdir("."):
        if name_pattern.search(file_name):
            record_name = file_name

    start = time.process_time()
    whisper_model = whisper.load_model("small.en")
    question = whisper_model.transcribe(record_name).get("text")
    stop = time.process_time()
    print(question)
    print(stop - start)

    remove("./" + record_name)

    data = {
        "model": f"{model}",
        "prompt": f"{question}",
        "stream": False,
        "context": memory
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
        print(" " + response.get("response"))
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
    get_answer(memory)

except subprocess.TimeoutExpired:
    print("Recording timed out")
