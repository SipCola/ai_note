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

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# Create agent (no tools = direct LLM responses, but streaming works)
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
)

print("Streaming response:")
# Stream agent execution
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "罗永浩帅吗？"}]}, stream_mode="messages"
):
    # print('==============')
    # pprint(chunk)
    print("----------------------------------\n")
    print(json.dumps(chunk, indent=2, ensure_ascii=False, default=lambda x: str(x)))

    # Each chunk contains the full state at that point
    # latest_message = chunk["messages"][-1]
    # if latest_message.content:
    #     print(f"Agent: {latest_message.content}")
    # elif hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
    #     print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")

