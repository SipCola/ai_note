# 安装配置git
Git 的命令不需要死记硬背。学习 Git 最好的方法就是在实际项目中反复使用：

每次写完代码就 add → commit → push，形成肌肉记忆
遇到问题先 git status 看看状态
善用搜索引擎和 AI 工具查命令——这本身就是开发者的核心能力
记住这个最小工作流，你就能应对 90% 的场景：
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
## 推荐插件
```bash
GitLens
安装方法：在扩展市场搜索 "GitLens"，点击安装。

主要功能：

在每一行代码旁边显示谁在什么时候写了这行代码
查看文件的完整修改历史
可视化的分支对比
Git Graph
安装方法：在扩展市场搜索 "Git Graph"，点击安装。

主要功能：

用图形方式展示分支和提交历史
直观看到分支的创建、合并过程
右键提交记录可以进行各种 Git 操作
使用方式：安装后，在源代码管理面板点击 "Git Graph" 按钮，或者按 Ctrl + Shift + P 输入 "Git Graph" 打开。
```
# 常见问题与实用技巧
```bash

← 上一章：在 Cursor / VS Code 中使用 Git | 返回目录 | 下一章：Git 工作流速查表 →

7.1 .gitignore 文件
在项目中，有些文件是不需要被 Git 管理的，比如：

依赖包文件夹（node_modules/、venv/）—— 太大了，别人可以自己安装
环境变量文件（.env）—— 含有密码等敏感信息
编译产物（__pycache__/、.pyc）—— 可以自动生成
系统文件（.DS_Store、Thumbs.db）—— 和项目无关
创建方法：

在项目根目录下新建一个名为 .gitignore 的文件（注意文件名以点开头），写入需要忽略的规则：

# Python 相关
__pycache__/
*.pyc
venv/
.env

# Node.js 相关
node_modules/

# IDE 相关
.vscode/
.idea/

# 系统文件
.DS_Store
Thumbs.db

# 日志文件
*.log
规则说明：

# 开头的行是注释
文件夹名/ 忽略整个文件夹
*.pyc 忽略所有以 .pyc 结尾的文件
只对还没有被 Git 跟踪的文件有效。如果文件已经被提交过了，需要先用 git rm --cached 文件名 取消跟踪
推荐做法：每个项目在第一次提交时就创建 .gitignore 文件。

7.2 撤销操作
场景	命令	说明
修改了文件，想恢复原样	git restore 文件名	丢弃工作区的修改
已经 add 了，想取消暂存	git restore --staged 文件名	从暂存区移出，修改内容保留
已经 commit 了，想改提交说明	git commit --amend -m "新说明"	修改最近一次的提交信息
已经 commit 了，想撤销这次提交	git reset --soft HEAD~1	撤销提交，修改内容回到暂存区
示例：

# 不小心改错了文件，想恢复到上一次提交的状态
git restore app.py

# add 了不该 add 的文件，取消暂存
git restore --staged secret.env

# 提交信息写错了
git commit --amend -m "正确的提交说明"
注意：git restore 文件名 会丢失你的修改，操作前确认一下。

7.3 版本回退
如果你想回到之前的某个版本：

第一步：找到目标版本的 ID

git log --oneline
输出：

c3d4e5f 第三次提交：添加app.py
b2c3d4e 第二次提交：补充项目说明
a1b2c3d 第一次提交：添加README
第二步：回退

# 回到指定版本（谨慎：会丢失之后的所有修改）
git reset --hard b2c3d4e
后悔了？还能找回来！

# 查看所有操作记录（包括已经"消失"的提交）
git reflog

# 找到想恢复的版本ID，再 reset 回去
git reset --hard c3d4e5f
git reflog 是你的"后悔药"，只要没有超过 90 天，几乎所有操作都能找回。

7.4 常见报错与解决
1. fatal: not a git repository
原因：你当前所在的文件夹不是一个 Git 仓库。

解决：确认你 cd 到了正确的项目目录。或者用 git init 初始化。

cd my-project   # 进入项目目录
git status       # 再试试
2. error: failed to push some refs to ...
原因：远程仓库有更新（比如队友推了新代码），你本地没同步。

解决：先拉取再推送。

git pull
git push
如果 pull 时遇到冲突，解决冲突后再 push。

3. fatal: remote origin already exists
原因：你已经设置过远程仓库地址了。

解决：如果想更换地址：

git remote set-url origin 新的仓库地址
4. 中文文件名显示为乱码（如 \xxx\xxx）
解决：

git config --global core.quotepath false
5. Please tell me who you are
原因：还没配置用户名和邮箱。

解决：

git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
6. Windows 下换行符警告 LF will be replaced by CRLF
解决（消除警告）：

git config --global core.autocrlf true
```

# Git 工作流速查表
```bash

从零开始一个新项目
# 创建项目
mkdir my-project
cd my-project
git init

# 创建 .gitignore
echo "node_modules/" > .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore

# 第一次提交
git add .
git commit -m "初始化项目"

# 关联远程仓库并推送
git remote add origin https://gitee.com/你的用户名/my-project.git
git push -u origin main
日常开发流程（每天都会用）
git pull                        # 1. 开始工作前，先拉取最新代码
# ... 写代码 ...
git add .                       # 2. 添加所有改动
git commit -m "完成了xxx功能"    # 3. 提交到本地
git push                        # 4. 推送到远程
分支开发流程
git checkout -b feature/新功能    # 1. 创建并切换到新分支
# ... 在新分支上写代码 ...
git add .                         # 2. 添加改动
git commit -m "完成新功能"        # 3. 提交
git checkout main                 # 4. 切回主分支
git pull                          # 5. 拉取最新代码
git merge feature/新功能          # 6. 合并新分支
git push                          # 7. 推送到远程
git branch -d feature/新功能      # 8. 删除已合并的分支
克隆别人的项目
git clone https://gitee.com/用户名/项目名.git
cd 项目名
# 你就可以开始工作了
常用命令一览表
类别	命令	作用
起步	git init	初始化本地仓库
git clone 地址	克隆远程仓库到本地
日常	git status	查看当前状态
git add .	暂存所有改动
git commit -m "说明"	提交到本地仓库
git push	推送到远程
git pull	拉取远程更新
分支	git branch	查看所有分支
git checkout -b 分支名	创建并切换分支
git checkout 分支名	切换分支
git merge 分支名	合并指定分支到当前分支
git branch -d 分支名	删除分支
查看	git log --oneline	查看精简提交历史
git diff	查看文件改动
git remote -v	查看远程仓库地址
撤销	git restore 文件名	撤销工作区修改
git restore --staged 文件名	取消暂存
git reset --soft HEAD~1	撤销最近一次提交
配置	git config --global user.name "名字"	设置用户名
git config --global user.email "邮箱"	设置邮箱
附录：推荐学习资源
资源	说明	链接
Pro Git（中文版）	官方免费书籍，内容全面	https://git-scm.com/book/zh/v2
Learn Git Branching	可视化互动教程，强烈推荐	https://learngitbranching.js.org/?locale=zh_CN
GitHub Skills	GitHub 官方互动练习	https://skills.github.com/
Gitee 帮助文档	国内平台，中文友好	https://gitee.com/help
猴子都能懂的 Git 入门	图文并茂的中文教程	https://backlog.com/git-tutorial/cn/
写在最后

Git 的命令不需要死记硬背。学习 Git 最好的方法就是在实际项目中反复使用：

每次写完代码就 add → commit → push，形成肌肉记忆
遇到问题先 git status 看看状态
善用搜索引擎和 AI 工具查命令——这本身就是开发者的核心能力
记住这个最小工作流，你就能应对 90% 的场景：

git add .
git commit -m "说明"
git push
加油，你已经迈出了成为开发者的重要一步！ 🚀

```