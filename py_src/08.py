import os
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv('ARK_API_KEY')

SYSTEM_PROMPT = """你是一位精通天气预报的专家，说话喜欢用谐音梗或幽默的口吻。

你可以使用以下两个工具：
- get_weather_for_location: 用于查询特定城市的天气。
- get_user_location: 用于获取当前用户所在的地理位置。

如果用户询问天气，请确保你知道具体地点。如果从问题中可以看出用户指的是他们所在地，请先使用 get_user_location 工具获取位置。"""

@dataclass
class Context:
    """自定义运行时上下文架构。"""
    user_id: str

@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气情况。"""
    return f"{city} 天气晴朗，阳光明媚，非常适合出门玩耍！"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 检索用户信息。"""
    user_id = runtime.context.user_id
    return "佛罗里达" if user_id == "1" else "旧金山"

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
)

config = {"configurable": {"thread_id": "1"}}
ctx = Context(user_id="1")

print("Streaming agent execution:\n")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=ctx,
    stream_mode="values"
):
    if "messages" in chunk:
        latest_msg = chunk["messages"][-1]
        msg_type = latest_msg.__class__.__name__
        
        if latest_msg.content:
            print(f"[{msg_type}] {latest_msg.content}")
        elif hasattr(latest_msg, 'tool_calls') and latest_msg.tool_calls:
            # Fix: tool_calls is list of dicts, use tc["name"]
            tools = [tc["name"] for tc in latest_msg.tool_calls]
            print(f"[{msg_type}] Calling tools: {tools}")
        else:
            print(f"[{msg_type}]")
