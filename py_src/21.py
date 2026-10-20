import os
import asyncio
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    # 一行代码替代所有的 stdio/ClientSession 管理
    client = MultiServerMCPClient({
        "weather": {
            "transport": "stdio",
            "command": "python",
            "args": [os.path.abspath("20.py")],
            "env": os.environ.copy()
        }
    })

    # 获取工具
    tools = await client.get_tools()

    # 初始化模型
    llm = ChatOpenAI(
        model="doubao-seed-1-6-251015",
        temperature=0,
        api_key=os.getenv("ARK_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )

    # 创建 Agent（一句话）
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="你是智能助手小宁。请使用 query_weather 查询北京天气。",
    )

    # 执行
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "北京天气怎么样？"}]
    })

    print(f"回答: {response['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())