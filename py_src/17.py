import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ARK_API_KEY')

# --- 1. 定义生命周期钩子处理器 ---
class LifecycleHandler(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        """对应 before_agent: 代理整体流程开始"""
        print(f"\n🚀 [before_agent] 代理准备出发！输入内容: {inputs.get('messages', [])[-1].content}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """对应 before_model: 模型调用前"""
        print(f"🧠 [before_model] 正在思考中... (准备调用模型)")

    def on_llm_end(self, response, **kwargs):
        """对应 after_model: 模型响应后"""
        # response 是 LLMResult 对象，包含生成的文本或工具调用
        print(f"✨ [after_model] 模型给出了回应。")

    def on_chain_end(self, outputs, **kwargs):
        """对应 after_agent: 代理整体流程结束"""
        print(f"🏁 [after_agent] 任务完成！最终输出: {outputs.get('messages', [])[-1].content}")

# --- 2. 基础配置与工具定义 ---
@dataclass
class Context:
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

SYSTEM_PROMPT = "你是一位精通天气的专家。用户问天气时，先用 get_user_location 获取位置，再查天气。"

llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 创建代理
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
)

# --- 3. 运行并注入回调 ---
config = {
    "configurable": {"thread_id": "1"},
    "callbacks": [LifecycleHandler()]  # 在这里注入生命周期钩子
}
ctx = Context(user_id="1")

print("--- 开始执行代理 ---")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "今天什么天气？"}]},
    config=config,
    context=ctx,
    stream_mode="values"
):
    pass # 具体的打印逻辑已由 LifecycleHandler 处理