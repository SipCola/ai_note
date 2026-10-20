import os
from dataclasses import dataclass
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import before_agent, after_agent, before_model, after_model, AgentState
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from dotenv import load_dotenv

load_dotenv()

# --- 1. 定义中间件钩子 ---

@before_agent
def on_agent_start(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("\n🚀 [before_agent] 代理引擎启动...")
    return None

@before_model(can_jump_to=["end"])
def on_model_start(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("\n🧠 [before_model] 准备询问模型下一步该做什么...")
    return None

@after_model
def on_model_complete(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    last_msg = state["messages"][-1]
    print(f"✨ [after_model] 模型决策完成。")
    
    # 打印工具调用详情
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        for tc in last_msg.tool_calls:
            print(f"🛠️  [Tool Call] 正在调用工具: {tc['name']} | 参数: {tc['args']}")
    elif last_msg.content:
        print(f"💬 [Final Response] 模型直接回复了文字。")
    return None

@after_agent
def on_agent_end(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("\n🏁 [after_agent] 代理执行完毕，清理现场。")
    return None

# --- 2. 工具定义 (带内部打印) ---

@dataclass
class Context:
    user_id: str

@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气情况。"""
    print(f"🏃 [Executing] 正在查询 {city} 的天气数据库...")
    return f"{city} 天气晴朗，心情指数 100 分！"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 检索用户信息。"""
    user_id = runtime.context.user_id
    loc = "佛罗里达" if user_id == "1" else "旧金山"
    print(f"🏃 [Executing] 正在根据 UserID:{user_id} 定位到: {loc}")
    return loc

# --- 3. 初始化代理 ---

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=os.getenv('ARK_API_KEY'),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

agent = create_agent(
    model=llm,
    system_prompt="你是一位幽默的天气专家。用户问天气时，请务必先用 get_user_location 获取位置，再用 get_weather_for_location 查天气。",
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    middleware=[on_agent_start, on_model_start, on_model_complete, on_agent_end]
)

# --- 4. 执行测试 ---

config = {"configurable": {"thread_id": "weather_chat_1"}}
ctx = Context(user_id="1")

print("--- 开始运行 ---")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "帮我看看我这儿天气咋样？"}]},
    config=config,
    context=ctx,
    stream_mode="values"
):
    # stream_mode="values" 会在状态更新时打印整条消息链
    pass