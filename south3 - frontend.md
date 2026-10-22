# html常见属性速查
|属性	|用在哪	|作用	|示例|
|-----|-----|-----|-----|
|href	|<a>	|链接地址	|<a href="https://example.com">|
|src	|<img/6a10331c5c14c6ef0af5df51/SupplementaryLearning7.0/raw/main/0基础入门-阅读资料/0基础-前端入门/>	|图片地址	|<img src="/6a10331c5c14c6ef0af5df51/SupplementaryLearning7.0/raw/main/0基础入门-阅读资料/0基础-前端入门/photo.jpg">|
|alt	|<img/6a10331c5c14c6ef0af5df51/SupplementaryLearning7.0/raw/main/0基础入门-阅读资料/0基础-前端入门/>	|图片替代文字	|<img/6a10331c5c14c6ef0af5df51/SupplementaryLearning7.0/raw/main/0基础入门-阅读资料/0基础-前端入门/ alt="头像">|
|target	|<a>	|打开方式	|<a target="_blank">|
|type	|<input>	|输入类型	|<input type="password">|
|placeholder	| <input>、<textarea>	|占位提示文字	|<input placeholder="请输入">|
|id	|所有标签	|唯一标识	|<div id="header">|
|class	|所有标签	|分类标识	|<div class="card">|
# 前置准备工作
安装node[nodejs官网](https://nodejs.org/zh-cn)
```bash
# 检查版本
node -v
npm -v

#在终端里，进入你想放项目的文件夹，然后执行：
npm create vue@latest my-app
执行后会问你一堆选项，全部选 No（按回车就是 No） 就好，我们要一个最干净的项目：

✔ Add TypeScript? … No
✔ Add JSX Support? … No
✔ Add Vue Router? … No
✔ Add Pinia? … No
✔ Add Vitest? … No
✔ Add an End-to-End Testing Solution? … No
✔ Add ESLint? … No
✔ Add Prettier? … No

#然后依次执行：
cd my-app #— 进入项目目录
npm install #— 安装项目依赖（第一次要等几十秒）
npm run dev #— 启动开发服务器
终端会显示类似这样的信息：

  VITE v6.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
打开浏览器，访问 http://localhost:5173/，看到 Vue 的欢迎页面，就说明成功了！
```
# npm run dev可能遇到的异常
```bash
#npm : 无法加载文件 C:\Program Files\nodejs\npm.ps1，因为在此系统上禁止运行脚本。有关详细信息，请参阅 https:/go.microsoft.com/fwlink/?LinkID=135170 中的 about_Executi （执行以下这条命令可以解决）
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
#临时有用关闭窗口失效
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

#'XXX' 不是内部或外部命令，也不是可运行的程序或批处理文件。缺少node_modules 文件夹
npm install

```
{{ }} 里面可以写数据名、表达式、调用方法，但不能写语句（比如 if、for）

# 创建一个组件
在 src/components/ 目录下新建一个文件 创建一个组件
在 src/components/ 目录下新建一个文件 MyButton.vue：

<template>
  <button class="my-btn">
    {{ text }}
  </button>
</template>

<script setup>
defineProps({
  text: String
})
</script>

<style scoped>
.my-btn {
  padding: 8px 20px;
  font-size: 15px;
  border: none;
  border-radius: 6px;
  background: #42b883;
  color: white;
  cursor: pointer;
}
.my-btn:hover {
  background: #359e6e;
}
</style>：
```html
<template>
  <button class="my-btn">
    {{ text }}
  </button>
</template>

<script setup>
defineProps({
  text: String
})
</script>

<style scoped>
.my-btn {
  padding: 8px 20px;
  font-size: 15px;
  border: none;
  border-radius: 6px;
  background: #42b883;
  color: white;
  cursor: pointer;
}
.my-btn:hover {
  background: #359e6e;
}
</style>
```
#使用组件
在 App.vue 里 import 它，然后直接在 <template> 中当标签用：
<template>
  <div>
    <h1>组件示例</h1>
    <MyButton text="点赞" />
    <MyButton text="收藏" />
    <MyButton text="分享" />
  </div>
</template>

<script setup>
import MyButton from './components/MyButton.vue'
</script>