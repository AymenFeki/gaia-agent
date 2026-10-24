import json
import os
import requests

API = "https://agents-course-unit4-scoring.hf.space"
os.makedirs("data/files", exist_ok=True)

questions = requests.get(f"{API}/questions", timeout=30).json()

with open("data/questions.json", "w") as f:
    json.dump(questions, f, indent=2)

print(f"Got {len(questions)} questions\n")

for q in questions:
    file_name = q.get("file_name") or ""
    print(f"[{q['task_id'][:8]}] file={file_name or '-'}")
    print(f"  {q['question'][:150]}\n")

    if file_name:
        r = requests.get(f"{API}/files/{q['task_id']}", timeout=60)
        if r.ok:
            with open(f"data/files/{file_name}", "wb") as out:
                out.write(r.content)
        else:
            print(f"  !! could not download file ({r.status_code})")