import json
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pprint import pprint

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ARK_API_KEY")

# Define system prompt
SYSTEM_PROMPT = "你是智能助手小宁"


api_key = os.environ["ARK_API_KEY"]
# 直接传入参数，无需os.environ
llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,  # 👈 直接传入API Key
    base_url="https://ark.cn-beijing.volces.com/api/v3",  # 👈 直接传入Base URL
)

# Define response format



# Create agent
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁？"}]},
)

print(response)
print("="*50)
pprint(response)
print("="*50)
# 这种方式可以将所有的 LangChain 消息对象强制转成字典，然后打印
print(json.dumps(response, indent=2, ensure_ascii=False, default=lambda x: str(x)))




