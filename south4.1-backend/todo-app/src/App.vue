<template>
  <div class="todo-app">
    <h1>待办事项</h1>

    <!-- 添加新待办 -->
    <div class="add-todo">
      <input
        v-model="newTitle"
        placeholder="输入新的待办事项..."
        @keyup.enter="addTodo"
      />
      <button @click="addTodo">添加</button>
    </div>

    <!-- 待办列表 -->
    <ul class="todo-list">
      <li v-for="todo in todos" :key="todo.id" :class="{ done: todo.done }">
        <input
          type="checkbox"
          :checked="todo.done"
          @change="toggleTodo(todo)"
        />
        <span>{{ todo.title }}</span>
        <button @click="removeTodo(todo.id)">删除</button>
      </li>
    </ul>

    <!-- 空状态 -->
    <p v-if="todos.length === 0" class="empty">暂无待办事项，添加一个吧！</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'

const todos = ref([])
const newTitle = ref('')

// 页面加载时获取所有待办
onMounted(async () => {
  await fetchTodos()
})

// 获取所有待办
async function fetchTodos() {
  const res = await axios.get(`${API}/todos`)
  todos.value = res.data
}

// 添加待办
async function addTodo() {
  if (!newTitle.value.trim()) return
  await axios.post(`${API}/todos`, { title: newTitle.value })
  newTitle.value = ''
  await fetchTodos()
}

// 切换完成状态
async function toggleTodo(todo) {
  await axios.put(`${API}/todos/${todo.id}`, { done: !todo.done })
  await fetchTodos()
}

// 删除待办
async function removeTodo(id) {
  await axios.delete(`${API}/todos/${id}`)
  await fetchTodos()
}
</script>

<style scoped>
.todo-app {
  max-width: 500px;
  margin: 40px auto;
  font-family: sans-serif;
}

.add-todo {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.add-todo input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.add-todo button {
  padding: 8px 20px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.todo-list {
  list-style: none;
  padding: 0;
}

.todo-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.todo-list li.done span {
  text-decoration: line-through;
  color: #999;
}

.todo-list li button {
  margin-left: auto;
  padding: 4px 12px;
  background: #ff5252;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty {
  text-align: center;
  color: #999;
  margin-top: 40px;
}
</style>