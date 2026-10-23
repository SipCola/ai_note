from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Todo API", description="一个简单的待办事项接口")


# ---------- 数据模型 ----------

class TodoCreate(BaseModel):
    """创建 Todo 时的请求体"""
    title: str
    description: str | None = None
    completed: bool = False


class TodoUpdate(BaseModel):
    """更新 Todo 时的请求体（所有字段可选）"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    """返回给客户端的 Todo 数据"""
    id: int
    title: str
    description: str | None = None
    completed: bool


# ---------- 内存存储 ----------

todos: dict[int, dict] = {}
next_id: int = 1


# ---------- 接口 ----------

@app.get("/todos", response_model=list[TodoResponse])
def list_todos(
    completed: bool | None = None,
    skip: int = 0,
    limit: int = 10,
):
    """获取 Todo 列表，支持按完成状态筛选和分页"""
    result = list(todos.values())
    if completed is not None:
        result = [t for t in result if t["completed"] == completed]
    return result[skip : skip + limit]


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """获取单个 Todo"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo 不存在")
    return todos[todo_id]


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    """创建新 Todo"""
    global next_id
    new_todo = {
        "id": next_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }
    todos[next_id] = new_todo
    next_id += 1
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate):
    """更新 Todo（局部更新）"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo 不存在")
    stored = todos[todo_id]
    update_data = todo.model_dump(exclude_unset=True)
    stored.update(update_data)
    return stored


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """删除 Todo"""
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo 不存在")
    del todos[todo_id]
    return {"message": f"Todo {todo_id} 已删除"}