<template>
  <div
    ref="rootRef"
    :class="['base-select', { 'base-select--open': listVisible, 'base-select--block': block }]"
  >
    <button
      ref="triggerRef"
      type="button"
      class="base-select__trigger"
      :aria-expanded="open"
      @click="toggle"
    >
      <span class="base-select__value">{{ currentLabel }}</span>
      <ChevronIcon :direction="open ? 'up' : 'down'" />
    </button>

    <Transition name="base-select-list" @after-leave="listVisible = false">
      <ul v-if="open" class="base-select__list">
        <li
          v-for="option in options"
          :key="option.value"
          :class="[
            'base-select__option',
            { 'base-select__option--active': isActive(option.value) }
          ]"
          @click="select(option.value)"
        >
          {{ option.label }}
        </li>
      </ul>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import ChevronIcon from '@/components/ui/ChevronIcon.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: ''
  },
  block: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const open = ref(false)
const listVisible = ref(false)

const currentLabel = computed(() => {
  const active = props.options.find(o => o.value === props.modelValue)
  return active ? active.label : props.placeholder
})

function isActive(value) {
  return props.modelValue === value
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    listVisible.value = true
  }
}

function select(value) {
  emit('update:modelValue', value)
  open.value = false
}

function onDocumentClick(e) {
  if (!open.value || !rootRef.value) return
  if (!rootRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
})
</script>

<style scoped lang="scss">
.base-select {
  position: relative;
  display: inline-block;
}

.base-select--block {
  display: block;
}

.base-select__trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 9px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 8px;
  background-color: var(--dvijok-white);
  cursor: pointer;
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;
  color: var(--dvijok-text-secondary);
  text-align: left;
  transition:
    border-bottom-left-radius 0.18s ease,
    border-bottom-right-radius 0.18s ease;
}

.base-select--open .base-select__trigger {
  border-bottom-color: transparent;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.base-select__list {
  position: absolute;
  top: calc(100% - 1px);
  left: 0;
  right: 0;
  z-index: 10;
  list-style: none;
  margin: 0;
  padding: 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid var(--dvijok-text-secondary);
  border-top: none;
  border-radius: 0 0 8px 8px;
  background-color: var(--dvijok-white);
}

.base-select__option {
  padding: 10px 9px;
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;
  color: var(--dvijok-text-primary);
  cursor: pointer;
}

.base-select__option--active {
  background-color: var(--dvijok-choice-active);
}

.base-select-list-enter-active,
.base-select-list-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.base-select-list-enter-from,
.base-select-list-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
