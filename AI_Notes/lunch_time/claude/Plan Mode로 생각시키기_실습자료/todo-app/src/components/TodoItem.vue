<script setup>
import { ref } from 'vue'

const props = defineProps({
  todo: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['toggle', 'update', 'delete'])

const isEditing = ref(false)
const draft = ref(props.todo.text)

function startEdit() {
  draft.value = props.todo.text
  isEditing.value = true
}

function saveEdit() {
  const trimmed = draft.value.trim()
  if (trimmed && trimmed !== props.todo.text) {
    emit('update', trimmed)
  }
  isEditing.value = false
}

function cancelEdit() {
  isEditing.value = false
}
</script>

<template>
  <li class="todo-item" :class="{ done: todo.done }">
    <input
      type="checkbox"
      :checked="todo.done"
      @change="$emit('toggle')"
      aria-label="완료 체크"
    />

    <input
      v-if="isEditing"
      v-model="draft"
      type="text"
      class="edit-input"
      autofocus
      @keyup.enter="saveEdit"
      @keyup.esc="cancelEdit"
      @blur="saveEdit"
    />
    <span v-else class="todo-text" @dblclick="startEdit">
      {{ todo.text }}
    </span>

    <div class="todo-actions">
      <button
        v-if="!isEditing"
        type="button"
        class="edit-btn"
        aria-label="수정"
        @click="startEdit"
      >
        수정
      </button>
      <button
        type="button"
        class="delete-btn"
        aria-label="삭제"
        @click="$emit('delete')"
      >
        삭제
      </button>
    </div>
  </li>
</template>
