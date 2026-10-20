import os
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# --- 1. 修改系统提示词为中文 ---
SYSTEM_PROMPT = """你是一位专业的专业气象预报员，说话幽默且喜欢用双关语。

你可以使用以下两个工具：
- get_weather_for_location: 根据特定的城市名称获取天气信息。
- get_user_location: 获取当前用户的地理位置。

如果用户询问天气，请确保你知道具体位置。如果从问题中可以看出用户指的是他们所在的所在地，
请务必先使用 get_user_location 工具来查找他们的位置。"""

@dataclass
class Context:
    user_id: str

# --- 2. 修改工具描述为中文（大模型靠这个选工具） ---
@tool
def get_weather_for_location(city: str) -> str:
    """获取指定城市的当前天气。"""
    return f"{city} 总是阳光明媚，适合出门！"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 获取用户的地理位置。"""
    user_id = runtime.context.user_id
    # 保持逻辑不变，仅修改返回提示
    return "佛罗里达" if user_id == "1" else "旧金山"

api_key = os.environ.get("ARK_API_KEY")
llm = ChatOpenAI(
    model="doubao-seed-1-8-251228",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 创建 Agent
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
)

config = {"configurable": {"thread_id": "1"}}

# 运行测试
response = agent.invoke(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=Context(user_id="1")
)

print("----------------------------------\n")
print(json.dumps(response, indent=2, ensure_ascii=False, default=lambda x: str(x)))