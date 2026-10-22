# 五分钟跑通第一个 API
 使用uv安装包（也可以使用conda切换环境）
```bash
#安装uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#查看uv版本，如果无法识别uv，请完全退出编辑器再重进
uv --version
#初始化项目
uv init --python 3.10
#安装依赖（如果在用 uv：uv pip install fastapi uvicorn sqlmodel）
uv pip install fastapi uvicorn sqlmodel
#httpx 可选 在后续测试接口时可能用到。
pip install httpx

mkdir backend
cd backend
#在项目根目录创建 requirements.txt，写入：
fastapi
uvicorn
sqlmodel
#这个文件的作用是：别人拿到你的代码后，运行 pip install -r requirements.txt 就能一键安装所有依赖
#或者使用这行命令直接写入
echo "fastapi`nuvicorn`nsqlmodel" | Out-File requirements.txt -Encoding utf8
```

# 第一次启动项目

```bash
#在 backend/ 目录下创建 main.py，写入以下代码：
#或者直接输入这行命令
@'
app = FastAPI()

# 定义一个 GET 接口
@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}

# 带路径参数的接口
@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello, {name}!"}
'@ | Out-File -FilePath main.py -Encoding utf8

#启动项目
uv run uvicorn main:app --reload
#出现以下内容成功
...
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
...
#FastAPI 有一个超棒的功能——自动生成接口文档，网络原因可能不能正常使用，魔法上网可解决
#可以直接在这个页面上测试接口，不需要写前端代码打开浏览器，浏览器输入：
http://127.0.0.1:8000/docs
```