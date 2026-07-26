<template>
  <div
    :class="['base-choice', `base-choice--${shape}`, { 'base-choice--block': block }]"
    :style="{ gap }"
  >
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      :class="['base-choice__option', { 'base-choice__option--active': isActive(option.value) }]"
      :aria-pressed="isActive(option.value)"
      :style="optionStyle(option, isActive(option.value))"
      @click="select(option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Number, Array],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  shape: {
    type: String,
    default: 'rounded',
    validator: value => ['pill', 'rounded'].includes(value)
  },
  multiple: {
    type: Boolean,
    default: false
  },
  gap: {
    type: String,
    default: '17px'
  },
  block: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

function isActive(value) {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.includes(value)
  }
  return props.modelValue === value
}

function activeStyle(option) {
  const style = {}
  if (option.activeColor) style.color = option.activeColor
  if (option.activeBg) style.backgroundColor = option.activeBg
  if (option.activeBorder) style.borderColor = option.activeBorder
  return style
}

function optionStyle(option, active) {
  if (!option.color && !option.bg) {
    return active ? activeStyle(option) : null
  }
  const color = active ? option.bg : option.color
  const bg = active ? option.color : option.bg
  const style = {}
  if (color) {
    style.color = color
    style.borderColor = color
  }
  if (bg) style.backgroundColor = bg
  return style
}

function select(value) {
  if (props.multiple) {
    const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const index = current.indexOf(value)
    if (index === -1) current.push(value)
    else current.splice(index, 1)
    emit('update:modelValue', current)
  } else {
    emit('update:modelValue', value)
  }
}
</script>

<style scoped lang="scss">
.base-choice {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.base-choice--block {
  width: 100%;
  justify-content: space-between;
}

.base-choice__option {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: var(--dvijok-white);
  border: 1px solid var(--dvijok-text-secondary);
  color: var(--dvijok-text-secondary);
  font-size: 12px;
  font-weight: 600;
  line-height: 15px;
  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease;
}

.base-choice--rounded .base-choice__option {
  padding: 8px 15px;
  border-radius: 8px;
}

.base-choice--pill .base-choice__option {
  padding: 9px 25px;
  border-radius: 50px;
}

.base-choice__option--active {
  background-color: var(--dvijok-choice-active);
  border-color: var(--dvijok-blue-primary);
  color: var(--dvijok-blue-primary);
}

.base-choice__option:hover:not(.base-choice__option--active) {
  border-color: var(--dvijok-bg-dark);
  color: var(--dvijok-bg-dark);
}
</style>
