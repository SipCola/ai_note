<template>
    <div class="message" :class="role">
      <div class="avatar">{{ role === 'user' ? '🧑' : '🤖' }}</div>
      <div class="bubble">{{ content }}</div>
    </div>
  </template>
  
  <script setup>
  defineProps({
    content: String,
    role: String   // 'user' 或 'assistant'
  })
  </script>
  
  <style scoped>
  .message {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    max-width: 80%;
  }
  
  .message.user {
    flex-direction: row-reverse;
    margin-left: auto;
  }
  
  .message.assistant {
    margin-right: auto;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
  }
  
  .message.user .avatar {
    background: #4a90d9;
  }
  
  .bubble {
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 15px;
    line-height: 1.6;
    word-break: break-word;
    white-space: pre-wrap;
  }
  
  .message.user .bubble {
    background: #4a90d9;
    color: #fff;
    border-top-right-radius: 4px;
  }
  
  .message.assistant .bubble {
    background: #fff;
    color: #333;
    border-top-left-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  </style>