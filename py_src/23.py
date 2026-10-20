import asyncio
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 引入核心组件
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession # 必须引入这个

load_dotenv()

async def main():
    # 1. 建立 SSE 连接
    async with sse_client("http://localhost:8000/sse") as (read, write):
        # 2. 核心修正：手动创建并初始化 Session
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. 此时 load_mcp_tools 只传这一个 session 对象
            mcp_tools = await load_mcp_tools(session)

            # 4. 初始化模型
            llm = ChatOpenAI(
                model="doubao-seed-1-6-251015",
                temperature=0,
                api_key=os.getenv("ARK_API_KEY"),
                base_url="https://ark.cn-beijing.volces.com/api/v3",
            )

            # 5. 创建 Agent
            agent = create_agent(
                model=llm,
                system_prompt="你是智能助手小宁。请使用 query_weather 查询北京天气。",
                tools=mcp_tools,
            )

            print("--- 正在通过 HTTP (SSE) Session 查询 ---")
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": "北京天气怎么样？"}]
            })

            print(f"回答: {response['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())