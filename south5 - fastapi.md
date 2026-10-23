# 五分钟跑通第一个 API
 使用uv安装包（也可以使用conda切换环境）
```bash
#安装uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#查看uv版本，如果无法识别uv，请完全退出编辑器再重进
uv --version
#初始化项目
uv init --python 3.10
#安装依赖
#httpx 可选 在后续测试接口时可能用到。
uv pip install fastapi uvicorn sqlmodel httpx
#创建项目文件
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

# Field() 进阶约束
```python
Field() 是 Pydantic 的字段约束工具，在类型之上添加业务规则：

from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="价格必须大于 0")
    quantity: int = Field(ge=0, le=9999, default=0)
    discount: float = Field(ge=0, le=1, default=1.0)
数值约束（gt、ge、lt、le）：

参数	含义	数学符号	示例	效果
gt	大于	>	Field(gt=0)	值必须 > 0
ge	大于等于	>=	Field(ge=0)	值必须 >= 0
lt	小于	<	Field(lt=100)	值必须 < 100
le	小于等于	<=	Field(le=100)	值必须 <= 100
字符串约束（min_length、max_length、pattern）：

参数	含义	示例	效果
min_length	最小长度	Field(min_length=1)	不能为空字符串
max_length	最大长度	Field(max_length=50)	最多 50 个字符
pattern	正则匹配	Field(pattern=r"^\d{11}$")	必须是 11 位数字
通用参数：

参数	含义	示例
default	默认值	Field(default=0)
description	字段描述（出现在 /docs 文档中）	Field(description="用户年龄")
examples	示例值（出现在文档中）	Field(examples=[25])
完整可运行示例
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class RegisterForm(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名，3-20 位，只能包含字母、数字、下划线",
    )
    password: str = Field(
        min_length=8,
        max_length=50,
        description="密码，至少 8 位",
    )
    age: int = Field(
        ge=1,
        le=150,
        description="年龄，1-150",
    )
    email: str = Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="邮箱地址",
    )
    phone: str = Field(
        pattern=r"^1[3-9]\d{9}$",
        description="手机号，11 位数字",
    )

@app.post("/register")
def register(form: RegisterForm):
    return {"message": "注册成功", "username": form.username}
```
# FastAPI 允许修改文档的访问路径，甚至关闭文档

# 依赖注入：Depends（处理函数）