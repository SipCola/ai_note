import json
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ARK_API_KEY")

SYSTEM_PROMPT = "你是智能助手小宁"

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

print("LLM streaming (typing effect):")
# Direct LLM stream for token-by-token
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "罗永浩帅吗？"}
]
for chunk in llm.stream(messages):


    # print("----------------------------------\n")
    # print(json.dumps(chunk, indent=2, ensure_ascii=False, default=lambda x: str(x)))

    if chunk.content:
        print(chunk.content, end='', flush=True)

print("\n\nAgent full response (non-streaming):")
