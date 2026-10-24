import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
API = "https://agents-course-unit4-scoring.hf.space"

with open("data/answers.json") as f:
    answers = json.load(f)

payload = {
    "username": os.environ["HF_USERNAME"],
    "agent_code": "https://github.com/<your-github-user>/gaia-agent",
    "answers": [{"task_id": k, "submitted_answer": v} for k, v in answers.items()],
}

r = requests.post(f"{API}/submit", json=payload, timeout=60)
print(r.status_code)
print(r.json())