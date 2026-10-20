import os
import json
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from dotenv import load_dotenv

# 1. 环境准备
load_dotenv()
api_key = os.getenv("ARK_API_KEY")
base_url = "https://ark.cn-beijing.volces.com/api/v3"

# 2. 定义上下文结构
class Context(TypedDict):
    user_role: str

# 3. 定义动态提示词函数
# 这个装饰器会让函数拦截请求，并根据 context 修改 System Prompt
@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:


    request_dict = vars(request)
    print(json.dumps(request_dict, indent=2, ensure_ascii=False, default=lambda x: str(x)))
    print("----------------------------------\n")

    """根据用户角色生成动态系统提示词"""
    # 💡 关键：从 request.runtime.context 获取 invoke 时传入的参数
    # 注意：在某些版本中，路径可能是 request.context 或 request.state["context"]
    # 按照你提供的参考片段，使用 request.runtime.context
    context = getattr(request.runtime, "context", {})
    user_role = context.get("user_role", "common")
    
    base_prompt = "你是智能助手小宁。"

    if user_role == "expert":
        print("--- [动态提示词] 当前角色：专家模式 (提供深度技术回答) ---")
        return f"{base_prompt} 你现在是资深技术专家，请提供详细、深度的专业回答。"
    elif user_role == "beginner":
        print("--- [动态提示词] 当前角色：小白模式 (解释通俗易懂) ---")
        return f"{base_prompt} 你现在是启蒙老师，请用最通俗易懂、大白话的方式解释概念。"
    
    return base_prompt

# 4. 初始化豆包模型
llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,
    api_key=api_key,
    base_url=base_url,
)

# 5. 创建 Agent (将动态提示词作为中间件传入)
agent = create_agent(
    model=llm,
    middleware=[user_role_prompt], # 👈 这里注入动态逻辑
    context_schema=Context         # 👈 定义 context 的类型约束
)

# 6. 运行案例：以“专家”身份询问
print("\n--- 第一次测试：专家模式 ---")
result_expert = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁"}]},
    context={"user_role": "expert"} # 👈 传入 context
)
print(f"专家回答: {result_expert['messages'][-1].content}")

# 7. 运行案例：以“小白”身份询问
# print("\n--- 第二次测试：小白模式 ---")
# result_beginner = agent.invoke(
#     {"messages": [{"role": "user", "content": "简单解释一下什么是大语言模型"}]},
#     context={"user_role": "beginner"} # 👈 传入 context
# )
# print(f"小白回答: {result_beginner['messages'][-1].content}")