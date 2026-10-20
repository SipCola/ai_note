import os
import time
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import (
    before_agent, 
    after_agent, 
    before_model, 
    after_model, 
    wrap_model_call,
    wrap_tool_call, 
    AgentState
)
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

# 加载环境变量
load_dotenv()

# --- 1. 定义中间件钩子 ---

@before_agent
def on_agent_start(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("\n🚀 [1. before_agent] 代理引擎启动...")
    return None

@wrap_model_call
def monitor_model(request: Any, next_call: Any) -> Any:
    """环绕模型调用：计算模型响应耗时"""
    # 这里的 request.state 包含了当前所有的消息记录
    print(f"⏳ [2. wrap_model_call] (进入) 正在请求 LLM...")
    start_time = time.time()
    
    # 执行真正的模型请求
    response = next_call(request)
    
    duration = time.time() - start_time
    print(f"⌛ [2. wrap_model_call] (退出) LLM 响应完成，耗时: {duration:.2f}s")
    return response

@before_model(can_jump_to=["end"])
def on_model_start(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("🧠 [3. before_model] 准备进入模型节点...")
    return None

@after_model
def on_model_complete(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print(f"✨ [4. after_model] 模型输出已存入状态。")
    return None

@wrap_tool_call
def secure_tool_executor(request: Any, next_call: Any) -> Any:
    """环绕工具调用：拦截或审计工具执行"""
    tool_name = request.state.get("tool_name", "unknown")
    print(f"🛡️ [5. wrap_tool_call] (进入) 安全审计工具: {tool_name}")
    
    try:
        # 执行真正的工具调用
        result = next_call(request)
        print(f"✅ [5. wrap_tool_call] (退出) 工具执行成功")
        return result
    except Exception as e:
        print(f"❌ [5. wrap_tool_call] (退出) 工具执行异常: {e}")
        return f"工具调用发生错误: {e}"

@after_agent
def on_agent_end(state: AgentState, runtime: ToolRuntime) -> dict[str, Any] | None:
    print("\n🏁 [6. after_agent] 代理所有任务已结束。")
    return None

# --- 2. 工具与环境配置 ---

@dataclass
class Context:
    user_id: str

@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气情况。"""
    print(f"🏃 [Tool Execution] 正在查询 {city} 的实时天气...")
    return f"{city} 天气晴朗，非常适合出门！"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 获取地理位置。"""
    user_id = runtime.context.user_id
    location = "佛罗里达" if user_id == "1" else "旧金山"
    print(f"🏃 [Tool Execution] 定位用户 {user_id} 为: {location}")
    return location

# --- 3. 初始化代理并注册中间件 ---

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=os.getenv('ARK_API_KEY'),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 注册 6 个钩子
agent = create_agent(
    model=llm,
    system_prompt="你是一位幽默的天气专家。请先获取用户位置，再查天气。",
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    middleware=[
        on_agent_start,
        monitor_model,      # wrap_model_call
        on_model_start,
        on_model_complete,
        secure_tool_executor, # wrap_tool_call
        on_agent_end
    ]
)

# --- 4. 执行流程 ---

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "weather_test_001"}}
    ctx = Context(user_id="1")

    print("--- 启动对话流 ---")
    inputs = {"messages": [{"role": "user", "content": "帮我看看我现在这儿天气咋样？"}]}
    
    for chunk in agent.stream(
        inputs,
        config=config,
        context=ctx,
        stream_mode="values"
    ):
        if "messages" in chunk:
            last_msg = chunk["messages"][-1]
            # 在 LangChain 中，AIMessage 的 type 为 'ai'
            if last_msg.content and last_msg.type == "ai":
                print(f"\n📢 [最终回答]: {last_msg.content}")

    print("\n--- 演示结束 ---")