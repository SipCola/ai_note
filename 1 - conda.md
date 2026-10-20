# 1、卸载python
- 打开“设置” → “应用” → “安装的应用”，搜 Python，点右边 ... → 卸载。有多个版本就逐个卸。
- 如果列表里找不到（比如绿色版/解压版），那就直接删掉它的安装文件夹，再清理一下环境变量里的 Python 路径

# 2、安装conda
- 方便进行版本管理
- [访问清华网站下载conda](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/)
- [已下载](sourse\Miniconda3-latest-Windows-x86_64.exe)
1. 下载 Miniconda3-latest-Windows-x86_64.exe
2. 双击运行安装程序
    * 安装避坑
        + install for:\
            选择Just Me：conda安装在用户目录下，避免需要管理员权限的各种错误和麻烦
3. 安装路径建议保持默认，或选择一个没有中文和空格的路径（如 D:\Miniconda3）
4. 勾选 "Add Miniconda3 to my PATH environment variable"（虽然安装器提示不推荐，但对初学者更方便）,勾选"Rigister Miniconda3 as my default Python 3.x"(必选：让vsc等编辑器能自动识别它)
![](sourse\conda-advanced-opt.PNG)
5. 安装完成后，打开 Anaconda Prompt（开始菜单搜索）或 PowerShell，验证安装：
```bash
conda --version 
#输出类似：conda 24.x.x
```
## 如果在 PowerShell 中使用 Conda，需要先初始化：
PowerShell 与 CMD 的区别
- CMD (命令提示符): 诞生于 80 年代，非常老旧，主要为了兼容 DOS 时代的简单命令。它的功能很弱，只能做简单的文件操作。
- PowerShell: 微软在 2006 年推出的现代化工具。它不仅仅是命令行，还是一个强大的自动化脚本引擎。它可以直接控制 Windows 的深层设置（比如注册表、服务、用户管理）。
```bash
conda init powershell
#然后重启 PowerShell，才能正常使用 conda activate。
```
# 3、验证安装
- win+R ，输入cmd
```bash
conda --version 
#输出类似：conda 24.x.x
```
# 3.1、配置conda环境
## 移除清华源（如果有）配置中科大镜像源
```bash
#如无请忽略
conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --remove channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --remove channels defaults
conda clean -i

# 方式一：添加中科大的源
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/

# 搜索时显示频道地址
conda config --set show_channel_urls yes

# 移除默认的 defaults 频道（可选，避免仍然请求国外源）
conda config --remove channels defaults
验证镜像是否生效：
conda config --show channels

方式二：直接用官方的源(如果网速太慢、卡住，需要开启梯子。)
#一键恢复默认源
conda config --remove-key channels
```
# 4、通过conda安装python
```bash
# 创建环境并指定 Python 版本
conda create -n myproject python=3.12
# myproject填自己的文件名
conda create -n ai_agent python=3.12
```
- 现推荐python=3.12，主流框架基本支持

```bash
# 激活环境
conda activate myproject
# 进入其他环境
conda activate ai_agent
# 检查py版本
python --version
# 进入环境后，使用pip装包，因为pip的ai库更全更新
pip install openai
# 退出当前环境，回到 base
conda deactivate
# 退出 base 环境
conda deactivate
```
```bash
查看环境：
# 列出所有环境（* 标记当前激活的环境）
conda env list
# 或
conda info --envs

# 输出示例：
# base                  *  C:\Users\xxx\Miniconda3
# myproject                C:\Users\xxx\Miniconda3\envs\myproject
# data_env                 C:\Users\xxx\Miniconda3\envs\data_env
```
```bash
删除环境：
conda env remove -n myproject

# 或删除指定路径的环境
conda env remove --prefix ./envs
```
```bash
克隆环境：
# 基于已有环境克隆一个新环境
conda create -n myproject_copy --clone myproject
```
## python的虚拟环境和conda有什么区别
- Vene创建环境只是复制或链接了系统现有的py解释器
- 只隔离了第三方包
- 局限性
    - 必须依赖宿主：电脑装了哪个版本的，你才能创建哪个版本
    - 只能管理python：如果需要C语言等其他库，venv有时候搞不定，得系统自己装


# 安装编辑器
cursor
https://cursor.com/home?from=agents

# cursor中设置conda环境
- ctrl shift p 搜索python解释器（或者Python: Select Interpreter），选择对应环境，如果重新进入后任然没有进入正确的环境，则每次进入时终端输入
```bash
#每次进入编辑器输入
conda activate myproject
#运行py代码
python ./1.py
```

# 为何ai应用开发不用conda
- conda适用于机器学习，一键安装本地模型所需的环境，但对于ai应用开发来说非常重
- 如果做模型微调可以使用conda
- 应用的部署应该容器化，轻量，可弹性扩展

# 使用conda安装包
```bash
conda install fastapi
#查看安装的包
conda list
#仅查看用户手动安装的包
conda install fastapi
#查看安装的包在哪个路径下
python -c "import fastapi;print(fastapi.__file__)"
#移除 fastapi
conda remove fastapi 
```

# 使用pip安装包
```bash
#pip安装fastapi
pip install fastapi
#查看pip安装的包
pip list
#查看包安装的路径
pip show fastapi
#移除 fastapi
pip uninstall fastapi 
```
# 使用uv安装包
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
```