<script setup>
import { ref } from 'vue'

const emit = defineEmits(['add-todo'])
const text = ref('')

function submit() {
  const trimmed = text.value.trim()
  if (!trimmed) return
  emit('add-todo', trimmed)
  text.value = ''
}
</script>

<template>
  <form class="todo-input" @submit.prevent="submit">
    <input
      v-model="text"
      type="text"
      placeholder="할 일을 입력하세요"
      aria-label="할 일 입력"
    />
    <button type="submit">추가</button>
  </form>
</template>
