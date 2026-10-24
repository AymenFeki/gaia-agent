from dotenv import load_dotenv
from smolagents import LiteLLMModel

load_dotenv()

model = LiteLLMModel(model_id="gemini/gemini-3.8-flash")
reply = model([{"role": "user", "content": [{"type": "text", "text": "Say hi in 3 words."}]}])
print(reply.content)