import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI

load_dotenv()

# --- 时间追踪器 ---
class AgentTimer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.last_mark = self.start_time

    def mark(self, event_name):
        now = time.perf_counter()
        elapsed_total = now - self.start_time
        since_last = now - self.last_mark
        print(f"\n⏱️ [{elapsed_total:.3f}s] {event_name}")
        self.last_mark = now

timer = AgentTimer()

# --- 1. 系统提示词 ---
SYSTEM_PROMPT = """你是一个天气查询助手。
请遵循以下确定性操作：
- 如果没有城市名，请立即执行 get_user_location。
- 如果已有城市名，请立即执行 get_weather_for_location。
在得到最终天气结果后，直接回复天气信息。"""

@dataclass
class Context:
    user_id: str

# --- 2. 工具定义 ---
@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """获取用户当前城市(内部ID定位)。"""
    timer.mark("🛠️ 工具执行中: get_user_location")
    return "佛罗里达" if runtime.context.user_id == "1" else "旧金山"

@tool
def get_weather_for_location(city: str) -> str:
    """查询指定城市天气。"""
    timer.mark(f"🛠️ 工具执行中: get_weather_for_location (参数: {city})")
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

# --- 5. 运行并流式打印思考过程 ---
print("🚀 [0.000s] Agent 调用发起")
config = {"configurable": {"thread_id": "1"}}

# 使用 stream 模式获取中间环节
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=Context(user_id="1")
):
    # 遍历每个节点（agent 节点负责思考和决策，tools 节点负责执行）
    for node_name, output in chunk.items():
        if "messages" in output:
            last_msg = output["messages"][-1]
            
            # --- A. 打印豆包的“隐藏思考” (Reasoning Tokens) ---
            # 豆包 1.8 的推理内容通常在这个字段
            reasoning = last_msg.additional_kwargs.get("reasoning_content", "")
            if reasoning:
                print(f"\n🧠 【LLM 内部推理/Reasoning】:\n{reasoning}")

            # --- B. 打印工具调用决策 (Tool Calls) ---
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    print(f"\n🎯 【决策：调用工具】: {tc['name']} | 参数: {tc['args']}")

            # --- C. 打印最终回复内容 ---
            elif last_msg.content:
                print(f"\n💬 【最终回复】: {last_msg.content}")
        

        
        # --- D. 打印工具节点返回的原始结果 ---
        elif node_name == "tools":
             print(f"✅ 【工具返回结果】: {output}")

timer.mark("🏁 Agent 流程结束")