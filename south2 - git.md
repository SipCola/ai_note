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
# 分支
## 分支基本操作
```bash
查看当前分支
git branch
输出（* 标记当前所在的分支）：

* main
创建新分支
git branch feature/hello
这会创建一个名为 feature/hello 的新分支，但你还在 main 上。

切换分支
git checkout feature/hello
或者用更新的命令：

git switch feature/hello
```

# 5.3 在分支上工作并合并
完整流程演示：
```bash
# 1. 确保你在 main 分支上(checkout本意：结账离开，登记取出)
git checkout main

# 2. 创建并切换到新分支
git checkout -b feature/greeting

# 3. 在新分支上开发（创建一个新文件）
echo "def greet(): print('你好！')" > greeting.py

# 4. 提交改动
git add .
git commit -m "添加greeting功能"

# 5. 切回主分支
git checkout main

# 6. 你会发现 greeting.py 不见了！别担心，它在 feature/greeting 分支上

# 7. 把新分支的改动合并到主分支
git merge feature/greeting

# 8. 现在 greeting.py 出现在 main 分支上了！

# 9. 删除已合并的分支（可选，保持整洁）
git branch -d feature/greeting
```

# 处理合并冲突
```bash
什么时候会出现冲突？

当两个分支修改了同一个文件的同一行时，Git 不知道该保留哪个版本，就会产生"冲突"。

冲突长什么样？

打开有冲突的文件，你会看到类似这样的标记：

<<<<<<< HEAD
这是 main 分支的内容
=======
这是 feature 分支的内容
>>>>>>> feature/xxx
含义：

<<<<<<< HEAD 到 ======= 之间：当前分支（main）的内容
======= 到 >>>>>>> feature/xxx 之间：要合并进来的分支内容
怎么解决？

打开文件，手动决定保留哪部分（或者两部分都保留）
删除 <<<<<<<、=======、>>>>>>> 这些标记
保存文件
重新 add 和 commit
# 解决冲突后
git add .
git commit -m "解决合并冲突"
在 Cursor/VS Code 中解决冲突更方便——编辑器会高亮冲突区域，提供"接受当前" / "接受传入" / "接受两者"的按钮，点一下就行。
```

# 用图形界面完成 Git 操作
```bash
提交代码（代替命令行的 add + commit）
打开源代码管理面板（Ctrl + Shift + G）
你会看到所有被修改的文件列表
点击文件右边的 "+" 号，将文件添加到暂存区（相当于 git add）
或者点击 "更改" 右边的 "+" 一键暂存所有文件
在顶部的输入框中写提交说明
点击 "✓ 提交" 按钮（相当于 git commit）
推送和拉取
在源代码管理面板顶部的 "..." 菜单中，你可以找到：

推送（Push）：把本地提交推送到远程
拉取（Pull）：拉取远程最新代码
或者看状态栏（底部）：

如果显示 ↑1，表示有 1 个本地提交等待推送
如果显示 ↓2，表示远程有 2 个更新等待拉取
点击这些箭头图标可以直接执行推送/拉取
切换分支
点击左下角状态栏上的分支名称（比如 main），会弹出分支列表，你可以：

选择已有分支进行切换
输入新名称创建新分支
解决冲突
当合并产生冲突时，Cursor / VS Code 会：

在冲突文件上标记 "C"（Conflict）
打开文件后，冲突区域会被高亮显示
每个冲突区域上方会显示操作按钮：
Accept Current Change（接受当前分支的改动）
Accept Incoming Change（接受合并进来的改动）
Accept Both Changes（两个都保留）
选择完毕后保存文件，然后暂存并提交
```