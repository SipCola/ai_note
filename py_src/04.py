import os
import json
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from dotenv import load_dotenv
from pprint import pprint

# 1. 加载环境变量
load_dotenv()
api_key = os.getenv("ARK_API_KEY")
base_url = "https://ark.cn-beijing.volces.com/api/v3"

# 2. 定义期望的输出结构 (使用 Pydantic)
class ContactInfo(BaseModel):
    """提取联系人信息的结构"""
    name: str = Field(description="人员姓名")
    email: str = Field(description="电子邮箱地址")
    phone: str = Field(description="电话号码")

# 3. 初始化豆包模型
llm = ChatOpenAI(
    model="doubao-seed-1-6-251015",
    temperature=0,  # 结构化输出建议将温度设为 0，保证稳定性
    api_key=api_key,
    base_url=base_url,
)

# 4. 创建具备结构化输出能力的 Agent
# 注意：ToolStrategy 会利用模型的“工具调用”能力来保证输出格式的准确性
agent = create_agent(
    model=llm,
    system_prompt="你是一个信息提取助手，负责从文本中精准提取联系人信息。",
    response_format=ToolStrategy(ContactInfo)
)

# 5. 调用 Agent
raw_text = "请从这里提取信息：张三，他的邮箱是 zhangsan@example.com，电话是 13800138000"
print(f"--- 正在处理文本 ---\n{raw_text}\n")

result = agent.invoke({
    "messages": [{"role": "user", "content": raw_text}]
})

# 6. 解析结果
# 核心：结构化后的数据存放在 result["structured_response"] 中
structured_data = result.get("structured_response")

print("="*50)
print("【结构化提取结果】")
if structured_data:
    print(f"姓名: {structured_data.name}")
    print(f"邮箱: {structured_data.email}")
    print(f"电话: {structured_data.phone}")
    
    # 它是一个 Pydantic 对象，也可以转成字典
    pprint(structured_data.model_dump())
else:
    print("未能成功提取结构化数据")
