import json
import os
import time

from agent import agent

with open("data/questions.json") as f:
    questions = json.load(f)

answers = {}
if os.path.exists("data/answers.json"):
    with open("data/answers.json") as f:
        answers = json.load(f)

FORMAT_RULES = """
Answer rules:
- Reply with ONLY the final answer, nothing else. No explanation, no full sentence, no "FINAL ANSWER".
- Numbers: digits only, no commas, no units unless the question asks for them.
- Lists: comma-separated, in the order the question asks for.
- Names and words: exactly as the question requests (e.g. "first name only" means one word).
- If you cannot find the answer, give your single best guess. Never answer "Unknown" or "not found".
"""

# --- Run the agent on each question ---
for q in questions:
    task_id = q["task_id"]

    if task_id in answers:
        print(f"[{task_id[:8]}] already answered, skipping")
        continue

    task = q["question"]
    if q.get("file_name"):
        task += f"\n\nThe attached file is at data/files/{q['file_name']}. Use the read_file tool to read it."
    task += "\n" + FORMAT_RULES

    print(f"\n[{task_id[:8]}] running...")
    try:
        result = agent.run(task)
        answers[task_id] = str(result).strip()
        print(f"[{task_id[:8]}] answer: {answers[task_id]}")
    except Exception as e:
        print(f"[{task_id[:8]}] FAILED: {e}")

    with open("data/answers.json", "w") as f:
        json.dump(answers, f, indent=2)

    time.sleep(5)

print(f"\nDone. {len(answers)} answers saved in data/answers.json")