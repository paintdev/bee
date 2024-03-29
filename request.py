import time
import requests
import json
from os import path, listdir, remove

import subprocess
from faster_whisper import WhisperModel
import re


python_path = ".venv\Scripts\python.exe"  # PATH to venv python
recorder_path = "./record.py"

model = "phi"
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
    whisper_model = WhisperModel("small.en")
    # whisper_model = WhisperModel("small.en", device="cuda", compute_type="float16")
    question, _ = whisper_model.transcribe(record_name, vad_filter=True)
    question = list(question)
    stop = time.process_time()
    print(question)
    print(f"Whisper took {stop - start:.1f} second(s)")

    question = str(question[0]).split(", ")[4][7:-1:1]
    print("Prompt: " + question)

    remove("./" + record_name)

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
        
        print("Response:")
        print(response.get("response"))
        duration = response.get("total_duration")
        print(f"{model} took {duration / 10**9}")
        memory = response.get("context")
        with open("memory.txt", "w") as file:
            file.write("")
            file.write(",".join(map(str, memory)))

    else:
        print("Request failed with status code:", response.status_code)


recording_process.wait(20)
get_answer(memory)
