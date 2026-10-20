import os
import time
import json
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI

load_dotenv()

# --- 时间追踪器：记录相对于启动时刻的偏移 ---
class AgentTimer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.last_mark = self.start_time

    def mark(self, event_name):
        now = time.perf_counter()
        elapsed_total = now - self.start_time
        since_last = now - self.last_mark
        print(f"⏱️ [{elapsed_total:.3f}s] {event_name} (距离上一阶段: {since_last:.3f}s)")
        self.last_mark = now

timer = AgentTimer()

# 混合了结构化与自然语言引导，减少模型推理负担
SYSTEM_PROMPT = """你是一个天气查询助手。
请遵循以下确定性操作：
- 如果没有城市名，请立即执行 get_user_location。
- 如果已有城市名，请立即执行 get_weather_for_location。

不要输出任何思考过程，直接返回工具调用。在得到最终天气结果后，直接回复天气信息。"""

@dataclass
class Context:
    user_id: str

# --- 2. 工具定义：在入口处记录时间 ---
@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """获取用户当前城市(内部ID定位)。""" # 👈 缩短描述，直击要点
    timer.mark("➡️ 工具开始执行: get_user_location")
    return "佛罗里达" if runtime.context.user_id == "1" else "旧金山"

@tool
def get_weather_for_location(city: str) -> str:
    """查询指定城市天气。参数:city(str)。""" # 👈 明确参数类型，减少模型犹豫
    timer.mark(f"➡️ 工具开始执行: get_weather_for_location (参数: {city})")
    return f"{city} 总是阳光明媚！"
# --- 3. 初始化 LLM ---
llm = ChatOpenAI(
    model="doubao-seed-1-8-251228",
    temperature=0,
    max_tokens=5000,
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# --- 4. 创建 Agent ---
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
)

# --- 5. 运行并分析流程耗时 ---
print("🚀 [0.000s] Agent 调用发起")
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=Context(user_id="1")
)

timer.mark("🏁 Agent 流程结束，返回最终答案")