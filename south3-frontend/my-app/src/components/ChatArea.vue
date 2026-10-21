<template>
    <main class="chat-area" ref="chatRef">
      <div v-if="messages.length === 0" class="empty-tip">
        发送一条消息开始对话吧 💬
      </div>
  
      <MessageBubble
        v-for="(msg, index) in messages"
        :key="index"
        :content="msg.content"
        :role="msg.role"
      />
  
      <div v-if="loading" class="loading">
        <span class="dot-animation">AI 正在思考</span>
      </div>
    </main>
  </template>
  
  <script setup>
  import { ref, watch, nextTick } from 'vue'
  import MessageBubble from './MessageBubble.vue'
  
  const props = defineProps({
    messages: Array,
    loading: Boolean
  })
  
  const chatRef = ref(null)
  
  // 每当消息列表变化，自动滚动到底部
  watch(
    () => props.messages.length,
    async () => {
      await nextTick()
      if (chatRef.value) {
        chatRef.value.scrollTop = chatRef.value.scrollHeight
      }
    }
  )
  </script>
  
  <style scoped>
  .chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }
  
  .empty-tip {
    text-align: center;
    color: #999;
    margin-top: 40vh;
    font-size: 16px;
  }
  
  .loading {
    text-align: center;
    color: #888;
    padding: 10px;
  }
  
  .dot-animation::after {
    content: '';
    animation: dots 1.5s infinite;
  }
  
  @keyframes dots {
    0%   { content: ''; }
    25%  { content: '.'; }
    50%  { content: '..'; }
    75%  { content: '...'; }
  }
  </style>