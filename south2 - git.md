# 安装配置git
## 下载git
打开 Git 官网下载页面：https://git-scm.com/downloads/win（一般选 64-bit Git for Windows Setup）
```bash
#如果安装了winget,使用此方式安装
winget install --id Git.Git -e --source winget
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
创建成功后复制，页面会显示一个仓库地址，类似：
https://gitee.com/你的用户名/my-first-project.git
https://github.com/你的用户名/my-first-project.git  #https://github.com/SipCola/ai_note.git

## 本地仓库关联远程仓库
```bash
回到你的终端（确保在项目目录下），输入：

git remote add origin https://gitee.com/你的用户名/my-first-project.git
#git remote add origin https://github.com/SipCola/ai_note.git
origin 是远程仓库的别名（约定俗成用 origin），后面是你刚才复制的地址。

检查是否关联成功：

git remote -v
输出：

origin  https://gitee.com/你的用户名/my-first-project.git (fetch)
origin  https://gitee.com/你的用户名/my-first-project.git (push)
```
## 推送代码到远程
```bash
首次推送：
#有些 Git 版本默认分支名是 master 而不是 main，你可以用 git branch 查看当前分支名，然后把命令中的 main 替换成对应的名称。
或者统一设置默认分支名为 main：
git config --global init.defaultBranch main
git push -u origin main #如果报错那么输入git push -u origin master
系统会提示你输入 Gitee/GitHub 的用户名和密码（或 Token）。输入后代码就推送到远程了。

-u 参数会建立本地分支和远程分支的关联，只需要在第一次推送时加上。
```

## 后续推送（已经关联过了）：
```bash
以后每次提交后，只需要简单地：
git push
```
## 从远程拉取代码
```bash
git pull —— 获取远程最新代码
当远程仓库有更新时（比如队友推送了新代码），用：

git pull
它会自动下载远程的最新改动并合并到你的本地。

git clone —— 克隆已有仓库
如果你想把别人的（或者自己在另一台电脑上的）项目下载到本地：

git clone https://gitee.com/用户名/仓库名.git
这个命令会在当前目录下创建一个新文件夹，里面就是完整的项目。

clone 和 init 的区别：

命令	使用场景
git init	在本地从零开始创建新仓库
git clone	把远程已有的仓库下载到本地
```
