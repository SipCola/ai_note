

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