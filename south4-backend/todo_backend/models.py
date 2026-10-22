from sqlmodel import SQLModel, Field


class TodoCreate(SQLModel):
    """创建 Todo 时的请求体模型"""
    title: str
    done: bool = False


class TodoUpdate(SQLModel):
    """更新 Todo 时的请求体模型"""
    title: str | None = None
    done: bool | None = None


class Todo(SQLModel, table=True):
    """Todo 数据库表"""
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False