<template>
  <div class="base-tabs" role="tablist" @keydown="onKeydown">
    <button
      v-for="(option, i) in options"
      :key="option.value"
      ref="tabRefs"
      type="button"
      role="tab"
      :tabindex="isActive(option.value) ? 0 : -1"
      :aria-selected="isActive(option.value)"
      :class="['base-tabs__tab', { 'base-tabs__tab--active': isActive(option.value) }]"
      @click="select(option.value)"
      @focus="onFocus(option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const tabRefs = ref([])

function isActive(value) {
  return props.modelValue === value
}

function select(value) {
  emit('update:modelValue', value)
}

function focusTab(index) {
  const el = tabRefs.value[index]
  if (el && typeof el.focus === 'function') el.focus()
}

function onFocus(value) {
  if (!isActive(value)) select(value)
}

function onKeydown(e) {
  const count = props.options.length
  if (!count) return
  const currentIndex = props.options.findIndex(o => o.value === props.modelValue)
  let nextIndex = currentIndex
  switch (e.key) {
    case 'ArrowRight':
    case 'ArrowDown':
      nextIndex = (currentIndex + 1) % count
      break
    case 'ArrowLeft':
    case 'ArrowUp':
      nextIndex = (currentIndex - 1 + count) % count
      break
    case 'Home':
      nextIndex = 0
      break
    case 'End':
      nextIndex = count - 1
      break
    default:
      return
  }
  e.preventDefault()
  select(props.options[nextIndex].value)
  requestAnimationFrame(() => focusTab(nextIndex))
}
</script>

<style scoped lang="scss">
.base-tabs {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 30px;
}

.base-tabs__tab {
  position: relative;
  padding: 10px 10px 20px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  line-height: 16px;
  font-weight: 400;
  color: var(--dvijok-text-secondary);
  transition: color 0.18s ease;

  &::after {
    content: '';
    position: absolute;
    left: 10px;
    right: 10px;
    bottom: 9px;
    height: 2px;
    background: var(--dvijok-blue-primary);
    opacity: 0;
    transition: opacity 0.18s ease;
  }
}

.base-tabs__tab--active {
  color: var(--dvijok-blue-primary);

  &::after {
    opacity: 1;
  }
}

.base-tabs__tab:hover:not(.base-tabs__tab--active) {
  color: var(--dvijok-bg-dark);
}
</style>
