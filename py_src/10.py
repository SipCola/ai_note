import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage  # 👈 langchain_core
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ARK_API_KEY")

SYSTEM_PROMPT = "你是智能助手小宁"

llm = ChatOpenAI(
    model="doubao-seed-1-8-251228",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 对话历史（BaseMessage 对象 ✅）
ai_msg = AIMessage(content="I'd be happy to help you with that question!")



messages = [
    SystemMessage(content=SYSTEM_PROMPT),  # 👈 用 SYSTEM_PROMPT
    HumanMessage(content="Can you help me?"),
    ai_msg,
    HumanMessage(content="Great! What's 2+2?"),
]

# pprint(messages)

# print("="*50)
# print(json.dumps(messages, indent=2, ensure_ascii=False, default=lambda x: str(x)))

# print("Messages:")
for msg in messages:
    print(f"{msg.__class__.__name__}: {msg.content}")

# 👈 直接 llm.invoke(messages) – 官方支持！
response = llm.invoke(messages)


print("="*50)
print(json.dumps(response, indent=2, ensure_ascii=False, default=lambda x: str(x)))