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
    user_id: str

@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气情况。
    
    Args:
        city: 城市名称，例如 "北京" 或 "上海"
    """
    return f"{city} 天气晴朗，阳光明媚，非常适合出门玩耍！"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 检索用户当前位置。
    
    Args:
        runtime: 运行时上下文，包含用户ID
    """
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

print("Streaming agent UPDATES (deltas only):\n")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=ctx,
    stream_mode="updates"
):
    for node_name, node_update in chunk.items():
        print(f"Node: {node_name}")
        print(json.dumps(node_update, indent=2, ensure_ascii=False, default=lambda x: str(x)))
        print("\n")

        if "messages" in node_update:
            for msg in node_update["messages"]:
                msg_type = msg.__class__.__name__
                if msg.content:
                    print(f"[{node_name} | {msg_type}] {msg.content}")
                elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tools = [tc["name"] for tc in msg.tool_calls]
                    print(f"[{node_name} | {msg_type}] Calling tools: {tools}")
                else:
                    print(f"[{node_name} | {msg_type}]")

