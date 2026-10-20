import os
from pprint import pprint
import time
import json
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver  
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
        print(f"⏱️ [{elapsed_total:.3f}s] {event_name} (距离上一阶段: {since_last:.3f}s)")
        self.last_mark = now

timer = AgentTimer()

# --- 1. 系统提示词 (简化了逻辑，不再要求先调位置工具) ---
SYSTEM_PROMPT = "你是一位专业的专业气象预报员。请使用 get_weather_info 获取天气信息。如果你不知道用户在哪，工具会自动处理。"

@dataclass
class Context:
    user_id: str

# --- 2. 合并后的超级工具 ---
@tool
def get_weather_info(runtime: ToolRuntime[Context], city: str = None) -> str:
    """获取天气信息。如果 city 为空，将自动根据当前用户 ID 识别位置。"""
    timer.mark(f"➡️ 超级工具 [get_weather_info] 开始执行 (输入城市: {city})")
    
    # 逻辑 A：如果模型没给城市，内部执行位置识别
    target_city = city
    if not target_city:
        user_id = runtime.context.user_id
        # 模拟内部位置查询逻辑
        target_city = "佛罗里达" if user_id == "1" else "旧金山"
        print(f"  [工具内部日志] 自动识别位置为: {target_city}")
    
    # 逻辑 B：执行天气查询
    result = f"{target_city} 总是阳光明媚！"
    
    return result

# --- 3. 初始化 LLM ---
llm = ChatOpenAI(
    model="doubao-seed-1-8-251228",
    temperature=0,
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# --- 4. 创建 Agent (只注册一个工具) ---
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather_info],
    context_schema=Context,
    checkpointer=InMemorySaver(), 
)

# --- 5. 运行并分析流程耗时 ---
print("🚀 [0.000s] Agent 调用发起 (已合并工具)")
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=Context(user_id="1")
)

timer.mark("🏁 Agent 流程结束，返回最终答案")

print("\n----------------------------------")
print(f"最终回答: {response['messages'][-1].content}")

# --- 6. 查看 Checkpointer 中的存储内容 ---
print("\n🔍 [检查点内容查询] ...")

# 使用 config 获取当前 thread_id 的最新状态
state = agent.get_state(config)



print("="*50)
print(f"线程 ID: {config['configurable']['thread_id']}")
print(f"当前节点: {state.next}") # 接下来要运行的节点（如果是结束了，这里通常为空）

print("\n--- 存储的消息历史 (Messages) ---")
for i, msg in enumerate(state.values["messages"]):
    # 打印消息类型、ID和内容片段
    print(f"[{i}] {msg.__class__.__name__} (ID: {msg.id}): {msg.content}")
    
    # 如果消息包含工具调用，也打印出来
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        print(f"    └─ 🛠️ 包含工具指令: {msg.tool_calls[0]['name']}")

print("\n--- 原始快照元数据 (Metadata) ---")
# 打印检查点的元数据，如时间戳、写操作记录等
print(json.dumps(state.metadata, indent=2, ensure_ascii=False))
print("="*50)

pprint(state.values)