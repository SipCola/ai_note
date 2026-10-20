
# 安装环境
```bash
conda create -n langchain python=3.13

conda activate langchain 

conda install langchain 
conda install langchain-openai

# 导出依赖文件
conda env export > environment.yml

# 同步conda依赖
conda env update -f environment.yml --prune
```
- 记得CTRL shift p选择python编译器

# 使用deepseek模型
```python
#.env文件内修改为
DEEPSEEK_API_KEY=密钥
#将下列代码改为
api_key = os.environ["DEEPSEEK_API_KEY"]
# 直接传入参数，无需os.environ
llm = ChatOpenAI(
    model="deepseek-flash",
    temperature=0,
    api_key=api_key,                    # 👈 直接传入API Key
    base_url="https://api.deepseek.com",  # 👈 直接传入Base URL
    extra_body={"thinking": {"type": "disabled"}},  # 👈 关键：关闭思考模式，deepseek的思考模式冲突
)
```

