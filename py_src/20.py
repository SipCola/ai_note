from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP
mcp = FastMCP("MyWeatherService")

# 2. 定义查天气工具
@mcp.tool()
def query_weather(city: str) -> str:
    """根据城市名称查询天气。"""
    # 模拟数据：你可以根据输入返回不同的结果
    if "北京" in city:
        return "北京天气：晴，气温 25°C，微风。"
    elif "上海" in city:
        return "上海天气：阴，气温 22°C，局部有小雨。"
    else:
        return f"暂时查不到 {city} 的天气，可能那里是世外桃源吧。"

if __name__ == "__main__":
    mcp.run()