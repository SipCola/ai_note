<template>
    <footer class="input-bar">
      <input
        class="input"
        v-model="inputText"
        placeholder="输入你的问题..."
        @keyup.enter="handleSend"
      />
      <button class="send-btn" @click="handleSend" :disabled="!inputText.trim()">
        发送
      </button>
    </footer>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const emit = defineEmits(['send'])
  const inputText = ref('')
  
  function handleSend() {
    const text = inputText.value.trim()
    if (!text) return
  
    emit('send', text)
    inputText.value = ''
  }
  </script>
  
  <style scoped>
  .input-bar {
    display: flex;
    gap: 10px;
    padding: 16px 20px;
    background: #fff;
    border-top: 1px solid #e0e0e0;
  }
  
  .input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 15px;
    outline: none;
    transition: border-color 0.2s;
  }
  
  .input:focus {
    border-color: #4a90d9;
  }
  
  .send-btn {
    padding: 12px 24px;
    background: #4a90d9;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .send-btn:hover:not(:disabled) {
    background: #357abd;
  }
  
  .send-btn:disabled {
    background: #a0c4e8;
    cursor: not-allowed;
  }
  </style>