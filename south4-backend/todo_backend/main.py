from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from database import create_db_and_tables, get_session, engine
from models import Todo, TodoCreate, TodoUpdate
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

def cors():
    #return   
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

cors()
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    with Session(engine) as session:
        db_todo = Todo.model_validate(todo)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo


@app.get("/")
def index():
    return {"message": "Todo 后台服务已启动"}

@app.get("/todos")
def get_todos():
    with Session(engine) as session:
        todos = session.exec(select(Todo)).all()
        return todos

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")
        return todo
        
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo_update: TodoUpdate):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")

        todo_data = todo_update.model_dump(exclude_unset=True)
        todo.sqlmodel_update(todo_data)

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    """删除一条待办事项"""
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="待办事项不存在")

        session.delete(todo)
        session.commit()
        return {"message": "删除成功"}
"""
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
    """