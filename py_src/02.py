import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
import json



# 加载环境变量
load_dotenv()
api_key = os.getenv("ARK_API_KEY")
base_url = "https://ark.cn-beijing.volces.com/api/v3"

# 定义模型
basic_model = ChatOpenAI(
    model="doubao-seed-1-6-lite-251015",
    temperature=0,
    api_key=api_key,
    base_url=base_url,
)

advanced_model = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0.5,
    api_key=api_key,
    base_url=base_url,
)


# 中间件 - 关键修复点
@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:

    request_dict = vars(request)
    print(json.dumps(request_dict, indent=2, ensure_ascii=False, default=lambda x: str(x)))
    print("----------------------------------\n")

    """动态模型选择"""
    # ✅ 修复1: 用 request.messages，不是 request.state.get()
    messages = request.messages
    message_count = len(messages)

    print(f"\n[中间件] 消息数: {message_count}")

    if message_count > 6:
        print("🚀 高级模型")
        model = advanced_model
    else:
        print("☁️ 基础模型")
        model = basic_model

    # ✅ 修复2: request.override(model=model)
    return handler(request.override(model=model))


# 创建 agent - 无工具纯聊天
agent = create_agent(
    model=basic_model,
    system_prompt="你是智能助手小宁",  # ✅ v1 用 system_prompt
    middleware=[dynamic_model_selection],  # ✅ 无 tools= 也能跑
)

# 运行 - ✅ 输入输出格式
if __name__ == "__main__":
    response = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好，我是小宁。"},
                {"role": "user", "content": "我想写 Agent 中间件"},
                {"role": "assistant", "content": "可以用 Python 实现。"},
                {"role": "user", "content": "你好帅啊"},
            ]
        }
    )

    print("\n" + "=" * 50)
    print("✅ 最终响应:")
    print(response["messages"][-1].content)  # ✅ 正确：AIMessage.content
    print("=" * 50)
