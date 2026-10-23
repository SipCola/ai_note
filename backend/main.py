from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}

@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/add/{a}/{b}")
def add(a: int, b: int):
    return {"result": a + b}

@app.get("/profile/{username}")
def get_profile(username: str, age: int = 18):
    return {
        "username": username,
        "age": age,
        "is_adult": age >= 18
    }

fake_users = {
    1: {"name": "张三", "age": 25},
    2: {"name": "李四", "age": 30},
}


@app.get("/users")
def list_users():
    """获取所有用户"""
    return fake_users


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """获取单个用户"""
    return fake_users.get(user_id, {"error": "用户不存在"})


@app.post("/users")
def create_user():
    """创建用户（后面会完善请求体）"""
    return {"message": "创建成功"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """删除用户"""
    return {"message": f"用户 {user_id} 已删除"}

@app.get("/search")
def search(
    keyword: str,                     # 必填
    page: int = 1,                    # 默认值 1
    page_size: int = 20,              # 默认值 20
    category: str | None = None,      # 可选
):
    result = {"keyword": keyword, "page": page, "page_size": page_size}
    if category:
        result["category"] = category
    return result

from datetime import date


@app.get("/reports")
def get_reports(
    start_date: date,                  # 必填，格式 YYYY-MM-DD
    end_date: date,                    # 必填
    department: str | None = None,     # 可选字符串
    include_detail: bool = False,      # 布尔值
    limit: int = 100,                  # 整数
):
    return {
        "start_date": start_date,
        "end_date": end_date,
        "department": department,
        "include_detail": include_detail,
        "limit": limit,
    }
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float
    description: str | None = None



@app.post("/items")
def create_item(item: Item):
    return {"message": "创建成功", "item": item}

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None


@app.put("/items/{item_id}")
def update_item(
    item_id: int,           # → 路径参数（出现在路径模板中）
    item: Item,             # → 请求体（Pydantic Model 类型）
    q: str | None = None,   # → 查询参数（既不在路径中，也不是 Model）
):
    result = {"item_id": item_id, "item": item}
    if q:
        result["q"] = q
    return result