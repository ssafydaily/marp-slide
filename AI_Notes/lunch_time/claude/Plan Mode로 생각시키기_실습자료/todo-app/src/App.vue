<script setup>
import { ref, computed, watch } from 'vue'
import TodoInput from './components/TodoInput.vue'
import TodoList from './components/TodoList.vue'

const STORAGE_KEY = 'todo-app:todos'

function loadTodos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch (e) {
    console.error('할 일 목록을 불러오지 못했습니다.', e)
    return []
  }
}

const todos = ref(loadTodos())

watch(
  todos,
  (value) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
  },
  { deep: true }
)

const remainingCount = computed(
  () => todos.value.filter((todo) => !todo.done).length
)

function addTodo(text) {
  todos.value.push({
    id: Date.now(),
    text,
    done: false,
  })
}

function toggleTodo(id) {
  const todo = todos.value.find((item) => item.id === id)
  if (todo) todo.done = !todo.done
}

function updateTodo(id, text) {
  const todo = todos.value.find((item) => item.id === id)
  if (todo) todo.text = text
}

function deleteTodo(id) {
  todos.value = todos.value.filter((item) => item.id !== id)
}
</script>

<template>
  <div id="app">
    <header class="app-header">
      <h1>할 일 목록</h1>
      <p class="remaining">{{ remainingCount }}개 남음</p>
    </header>

    <TodoInput @add-todo="addTodo" />

    <TodoList
      :todos="todos"
      @toggle-todo="toggleTodo"
      @update-todo="updateTodo"
      @delete-todo="deleteTodo"
    />

    <p v-if="todos.length === 0" class="empty">
      아직 등록된 할 일이 없습니다. 위 입력창에 할 일을 추가해 보세요.
    </p>
  </div>
</template>
