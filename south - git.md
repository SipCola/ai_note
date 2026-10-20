# 安装配置git
## 下载git
打开 Git 官网下载页面：https://git-scm.com/downloads/win（一般选 64-bit Git for Windows Setup）
```bash
#检查版本
git --version
```

## 首次配置（只需做一次）
```bash
#安装好 Git 后，你需要告诉 Git "你是谁"。这些信息会出现在你的每一次提交记录中
git config --global user.name "你的名字"    #git config --global user.name "SipCola"
git config --global user.email "你的邮箱"   #git config --global user.email "2011292709@qq.com"
#解决中文显示问题
git config --global core.quotepath false
#检查配置是否成功
git config --list
#记得按q键退出
```

##  注册 GitHub / Gitee 账号
推荐：注册 Gitee（国内访问快）
打开 https://gitee.com
点击右上角"注册"
填写用户名、邮箱、密码，完成注册
验证邮箱
可选：注册 GitHub
打开 https://github.com
点击 "Sign up"
按照提示填写信息完成注册
入门阶段推荐使用 HTTPS 方式连接远程仓库
# git仓库
## 创建本地仓库
```bash
#你可以在任何位置创建。打开终端，输入：
mkdir my-first-project
cd my-first-project

#初始化 Git 仓库
git init

```
- echo的使用
```bash
在终端或 Shell 脚本里，echo 是最基础的命令，用于在屏幕上打印文本或变量的值。

基础输出

bash
echo "Hello, World!"          # 输出：Hello, World!
name="Alice"
echo "Hello, $name"           # 输出：Hello, Alice（会替换变量）[reference:3]
控制输出格式

bash
echo -n "不换行输出"           # -n 选项：输出后不自动换行[reference:4]
echo -e "第一行\n第二行"       # -e 选项：让 \n 等转义字符生效，实现换行[reference:5]
写入文件（配合重定向）

bash
echo "新内容" > file.txt       # >：覆盖写入 file.txt[reference:6]
echo "追加内容" >> file.txt    # >>：追加到 file.txt 末尾[reference:7]
```

```bash
# 1. 创建项目并初始化
mkdir git-practice
cd git-practice
git init

# 2. 创建第一个文件并提交
echo "# 我的练习项目" > README.md
git add README.md
git add .   #如果修改了多个文件，可以使用这个命令一次性提交
git commit -m "第一次提交：添加README"  #后面的引号里是提交说明，用简短的文字描述你这次做了什么改动。

# 3. 修改文件
echo "这个项目用来练习 Git" >> README.md

# 4. 查看改动
git diff

# 5. 查看状态
git status

# 6. 提交修改
git add .
git commit -m "第二次提交：补充项目说明"

# 7. 创建新文件并提交
echo "print('Hello World')" > app.py
git add .
git commit -m "第三次提交：添加app.py"

# 8. 查看提交历史
git log --oneline
```
# 连接远程仓库
## 在 Github/Gitee 上创建远程仓库
创建成功后，页面会显示一个仓库地址，类似：
https://gitee.com/你的用户名/my-first-project.git