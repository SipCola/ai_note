# 使用uv安装包（也可以使用conda切换环境）
```bash
#安装uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#查看uv版本，如果无法识别uv，请完全退出编辑器再重进
uv --version
#初始化项目
uv init --python 3.10
#使用uv的环境运行python
uv run python --version
#pip安装fastapi
pip install fastapi
#查看pip安装的包
pip list
#查看包安装的路径
pip show fastapi
#移除 fastapi
pip uninstall fastapi 
#使用 uv 时，通常不需要手动“进入”或激活虚拟环境。uv 的设计理念就是让你省去激活这一步，直接运行命令即可。
#在包含 pyproject.toml 的项目目录下，直接使用：
uv run python main.py
# 或运行其他命令，如：
uv run uvicorn main:app

```
# 安装三个核心依赖
|包名	|作用|
|-|-|
|fastapi    |Python 的 Web 框架，用来写后台接口|
|uvicorn	|服务器，用来运行 FastAPI 程序|
|sqlmodel	|数据库工具，用 Python 类操作数据库（内部整合了 SQLAlchemy + Pydantic）|
|httpx(可选)	|httpx 在后续测试接口时可能用到。另外推荐安装一个数据库可视化工具 DB Browser for SQLite，可以直观地看到数据库里存了什么：下载地址：https://sqlitebrowser.org/dl/|
```bash

#安装依赖（如果在用 uv：uv pip install fastapi uvicorn sqlmodel）
pip install fastapi uvicorn sqlmodel
#httpx 可选 在后续测试接口时可能用到。
pip install httpx
```
# 创建项目文件夹
我们的项目最终长这样（先别急着全部创建，跟着教程一步步来）：
todo_backend/
├── main.py              # 入口文件：定义所有接口
├── models.py            # 数据模型：定义数据库表结构
├── database.py          # 数据库配置：连接数据库
├── requirements.txt     # 依赖清单
└── database.db          # SQLite 数据库文件（运行后自动生成）

```bash
# 创建项目文件夹
mkdir todo_backend
cd todo_backend
创建 requirements.txt
#在项目根目录创建 requirements.txt，写入：
fastapi
uvicorn
sqlmodel
这个文件的作用是：别人拿到你的代码后，运行 pip install -r requirements.txt 就能一键安装所有依赖
#或者使用这行命令直接写入
echo "fastapi`nuvicorn`nsqlmodel" | Out-File requirements.txt -Encoding utf8
```
# 第一次启动项目
```bash
#在 todo_backend/ 目录下创建 main.py，写入以下代码：

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "你好，这是我的第一个后台服务！"}
#或者直接输入这行命令
@'
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "你好，这是我的第一个后台服务！"}
'@ | Out-File -FilePath main.py -Encoding utf8

#启动项目（如果使用uv：uv run uvicorn main:app --reload）
uvicorn main:app --reload
#出现以下内容成功
...
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
...
#FastAPI 有一个超棒的功能——自动生成接口文档，网络原因可能不能正常使用，魔法上网可解决
#可以直接在这个页面上测试接口，不需要写前端代码打开浏览器，浏览器输入：
http://127.0.0.1:8000/docs
```
# 路由：URL 和函数的对应关系
```python
#"路由"就是：当用户访问某个 URL 时，程序应该执行哪个函数。
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "首页"}

@app.get("/about")
def about():
    return {"message": "关于我们"}

 
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"用户{user_id}"}
#http://127.0.0.1:8000/users/1 → {"user_id": 1, "name": "用户1"}
#http://127.0.0.1:8000/users/42 → {"user_id": 42, "name": "用户42"} 
```
## 第一点：@app.get("/items/{item_id}") 里的字符串是什么？
- 第一个参数是 URL 路径模式，不是磁盘路径，也不是文件位置。
- 第二个是传入调用函数的参数
- /users/{user_id}/posts 整体就是一个路径模式，FastAPI 拿它去和请求的 URL 做模式匹配。里面的成分只有两类：
固定段（路径模式）：users、posts —— 必须原样出现，不取值。
占位符（路径参数）：{user_id} —— 匹配任意一段，取值传给函数参数。

## 查询参数
```python
@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int, page: int = 1, keyword: str = None):
    return {"user_id": user_id, "page": page, "keyword": keyword}

# GET /users/42/posts?page=3&keyword=fastapi
# → user_id=42, page=3, keyword="fastapi"

- user_id 出现在路径模式的占位符里 → 路径参数。
- page、keyword 没有出现在占位符里，也没有显式声明 → 查询参数。

两者从 URL 不同部分取值，互不干扰。
```
## 请求体
```python
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {"id": next_id, "title": todo.title, "done": todo.done}
    fake_db.append(new_todo)
    next_id += 1
    return new_todo
#todo的参数类型是 Pydantic 模型（或 dict 等复合类型）→ 请求体
#它不是查询参数。调用时必须发 JSON body（如 {"title": "...", "done": false}），而不是拼在 URL 的 ? 后面。
#status_code=201是http状态码
```
## 数据库
- Python 自带 SQLite 支
- SQLModel 让你用 Python 类 来代替 SQL 语句，对 Python 开发者更友好：
```python
# 定义表
class Todo(SQLModel, table=True):
    #primary_key=True设置该字段为主键，由数据库自动维护生成，唯一值
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False

# 新增一条数据
todo = Todo(title="买牛奶")
session.add(todo)
session.commit()
```