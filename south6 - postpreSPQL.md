环境安装
安装数据库
https://www.postgresql.org/download/windows/
初始密码：123456
默认端口： 5432

安装过程中弹出一个stack builder直接点取消（新版本取消勾选即可）

左侧栏databasses处右键添加数据库

总之python中可以直接用代码连接数据库，只要填写以下内容
DATABASE_URL=postgresql+asyncpg://postgres:你的密码@localhost:5432/langgraphs_db
POSTGRES_URI=postgresql://postgres:你的密码@localhost:5432/langgraphs_db