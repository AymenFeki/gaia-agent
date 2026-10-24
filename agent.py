import os
import re
import time
import requests
from markdownify import markdownify

from ddgs import DDGS
from dotenv import load_dotenv
from smolagents import LiteLLMModel, CodeAgent, VisitWebpageTool, tool
import pandas as pd


load_dotenv()

@tool
def search_web(query: str) -> str:
    """Searches the web with DuckDuckGo and returns the top results (title, link and snippet).
    Args:
        query: The search query, e.g. 'Ballon d Or 2025 winner'. Keep it short and specific.
    """
    try:
        results = []
        for attempt in range(3):
            results = DDGS().text(query, max_results=5)
            if results:
                break
            time.sleep(3)
        if not results:
            return f"No results found for '{query}'. Try a shorter or different query."

        lines = []
        for i, r in enumerate(results, start=1):
            lines.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['body']}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Search failed for '{query}': {e}"

@tool
def read_file(path: str) -> str:
    """Reads an attached task file and returns its full contents as text.
    For Excel (.xlsx) and CSV files it returns the COMPLETE table (all rows and columns), so you do not need to open the file again with pandas.
    For text-based files (.py, .txt, .json) it returns the raw text. Use this whenever the task mentions an attached file.
    Args:
        path: The path to the file, e.g. 'data/files/abc.xlsx'.
    """
    extension = os.path.splitext(path)[1].lower()
    try:
        if extension == ".xlsx":
            df = pd.read_excel(path)
            return df.to_string()
        elif extension == ".csv":
            df = pd.read_csv(path)
            return df.to_string()
        else:
            with open(path, "r", encoding="utf-8") as f:
              return f.read()
    except Exception as e:
        return f"Failed to read file '{path}': {e}"
    
HEADERS = {"User-Agent": "gaia-agent/0.1 (HF Agents Course project)"}

@tool
def visit_webpage(url: str, start: int = 0) -> str:
    """Opens a webpage (works for Wikipedia) and returns its text as markdown, 20000 characters at a time.
    If the page is longer, call it again with a higher start value (e.g. 20000, 40000) to read the next part.
    Args:
        url: The full URL of the page.
        start: Character position to start reading from (default 0).
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        text = markdownify(r.text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        chunk = text[start:start + 20000]
        return f"[characters {start}-{start + len(chunk)} of {len(text)}]\n\n{chunk}"
    except Exception as e:
        return f"Error fetching {url}: {e}"
    
model = LiteLLMModel(model_id="gemini/gemini-3.5-flash-lite", reasoning_effort="low", num_retries=2, timeout=120)

agent = CodeAgent(
    model=model,
    tools=[search_web, visit_webpage, read_file],
    max_steps=10,
    additional_authorized_imports=["pandas", "math", "re", "json", "datetime"],
    use_structured_outputs_internally=True,
)

if __name__ == "__main__":
    print(agent.run("What is 2+2? Reply with only the number."))  