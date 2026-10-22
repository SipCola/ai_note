from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# ---------- 请求体模型 ----------

class TodoCreate(BaseModel):
    title: str
    done: bool = False


# ---------- 模拟数据库（用列表临时存储） ----------

fake_db: list[dict] = []
next_id = 1


# ---------- 接口 ----------

@app.get("/")
def index():
    return {"message": "Todo 后台服务已启动"}


@app.get("/todos")
def get_todos():
    return fake_db


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {"id": next_id, "title": todo.title, "done": todo.done}
    fake_db.append(new_todo)
    next_id += 1
    return new_todo


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in fake_db:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="待办事项不存在")