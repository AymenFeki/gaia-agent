# GAIA Agent: Hugging Face Agents Course, Unit 4

A tool-using AI agent built with [smolagents](https://github.com/huggingface/smolagents) that answers real-world questions from the [GAIA benchmark](https://huggingface.co/papers/2311.12983). Final project of the [Hugging Face Agents Course](https://huggingface.co/learn/agents-course).

## Result

| Metric | Value |
|---|---|
| Score | **75% (15 / 20 correct)** |
| Benchmark | 20 Level-1 questions from the GAIA validation set (course subset) |
| Pass threshold | 30% |
| Model | Gemini 3.5 Flash-Lite (free tier) |

Scored by the course's evaluation API with **exact-match** grading.

## How it works

The agent is a smolagents `CodeAgent`: at each step the LLM writes Python code that calls tools, the code runs in a sandboxed interpreter, and the output is fed back as an observation. This repeats until the agent calls `final_answer()`.

```
question ──► CodeAgent (Gemini via LiteLLM)
                 │  writes Python code each step
                 ▼
          ┌──────────────┬──────────────────┬──────────────┐
          │ search_web   │ visit_webpage    │ read_file    │
          │ (DuckDuckGo) │ (any page, incl. │ (.xlsx, .csv,│
          │              │  Wikipedia)      │  .py, .txt)  │
          └──────────────┴──────────────────┴──────────────┘
                 │  observations
                 ▼
            final_answer ──► answers.json ──► scoring API
```

### Tools

- **`search_web`**: DuckDuckGo search (via `ddgs`) returning numbered results with title, link and snippet. Retries automatically when DuckDuckGo rate-limits.
- **`visit_webpage`**: fetches a page, converts it to markdown and returns it in 20,000-character chunks with a `start` offset, so the agent can page through long Wikipedia articles.
- **`read_file`**: reads attached task files; Excel/CSV are returned as full tables via pandas.

## Project structure

```
gaia-agent/
├── agent.py            # tools, model and CodeAgent definition
├── run_eval.py         # runs the agent on all questions, saves answers
├── submit.py           # submits answers to the course scoring API
├── fetch_questions.py  # downloads the 20 questions from the course API
├── download_files.py   # downloads task attachments from the GAIA dataset
├── test_model.py       # quick check that the API key and model work
└── requirements.txt
```

`data/` (questions, attachments, answers) is intentionally **not committed**: the GAIA authors ask not to republish the dataset.

## Setup

Requires Python 3.12 and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/<your-user>/gaia-agent.git
cd gaia-agent
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=...   # from Google AI Studio (free tier works)
HF_TOKEN=...         # Hugging Face read token; needs access to the gated GAIA dataset
HF_USERNAME=...      # your Hugging Face username, used for submission
```

## Usage

```bash
python test_model.py        # 1. check the model responds
python fetch_questions.py   # 2. get the 20 questions
python download_files.py    # 3. get the attachments (xlsx, py, mp3, png)
python run_eval.py          # 4. run the agent; resumable
python submit.py            # 5. submit for scoring
```

`run_eval.py` saves after every question and skips questions that already have an answer, so an interrupted run (rate limit, crash, Ctrl+C) can be restarted without repeating work. To re-run a question, delete its entry from `data/answers.json`.

## Problems solved along the way

| Problem | Cause | Fix |
|---|---|---|
| Model wrote prose inside code blocks → `SyntaxError` | Gemini didn't reliably follow smolagents' text code-block format | `use_structured_outputs_internally=True` (thought and code returned as separate JSON fields) |
| Every Wikipedia page returned **403 Forbidden** | Built-in `VisitWebpageTool` sends no User-Agent header | Custom `visit_webpage` with a descriptive User-Agent |
| Searches randomly returned nothing | DuckDuckGo rate limiting | Retry loop with a short pause |
| Requests timed out or hung for minutes | Free-tier model overloaded (503 / timeouts) | Switched to a less loaded model; added `timeout` and `num_retries` |
| Agent looped trying variables like `observation` | Small models confuse observation text with Python variables | Explicit rule in the system prompt naming the mistake |
| Correct answers in the wrong format | Exact-match grading | Strict answer-format rules appended to every task |
| Course file endpoint returned 404 | Endpoint unavailable | Download attachments by name from the gated GAIA dataset (answers file never downloaded) |

## Limitations and next steps

The 5 missed questions are mostly ones the agent has no tool for:

- **Audio** (2 questions, `.mp3`): add a transcription tool (e.g. Gemini audio input or Whisper)
- **Image** (chess position): pass the image to a vision-capable model
- **Video** (YouTube): add a transcript tool; the bird-counting question needs actual video analysis

## Acknowledgements

- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course) and its scoring API
- [GAIA: A Benchmark for General AI Assistants](https://huggingface.co/papers/2311.12983) (Mialon et al., 2023)