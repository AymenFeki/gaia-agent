import json
import os
import shutil
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

load_dotenv()  # reads HF_TOKEN from .env

with open("data/questions.json") as f:
    questions = json.load(f)

os.makedirs("data/files", exist_ok=True)

for q in questions:
    file_name = q.get("file_name")
    if not file_name:
        continue
    try:
        path = hf_hub_download(
            repo_id="gaia-benchmark/GAIA",
            repo_type="dataset",
            filename=f"2023/validation/{file_name}",
        )
        shutil.copy(path, f"data/files/{file_name}")
        print(f"OK   {file_name}")
    except Exception as e:
        print(f"FAIL {file_name}: {e}")