<script setup>
import TodoItem from './TodoItem.vue'

defineProps({
  todos: {
    type: Array,
    required: true,
  },
})

defineEmits(['toggle-todo', 'update-todo', 'delete-todo'])
</script>

<template>
  <ul class="todo-list">
    <TodoItem
      v-for="todo in todos"
      :key="todo.id"
      :todo="todo"
      @toggle="$emit('toggle-todo', todo.id)"
      @update="(text) => $emit('update-todo', todo.id, text)"
      @delete="$emit('delete-todo', todo.id)"
    />
  </ul>
</template>
