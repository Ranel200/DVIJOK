<template>
  <div
    :class="[
      'base-choice',
      `base-choice--${shape}`,
      `base-choice--${variant}`,
      { 'base-choice--block': block, 'base-choice--disabled': disable }
    ]"
    :style="{ gap }"
  >
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      :class="['base-choice__option', { 'base-choice__option--active': isActive(option.value) }]"
      :aria-pressed="isActive(option.value)"
      :aria-disabled="disable || undefined"
      :tabindex="disable ? -1 : undefined"
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
  variant: {
    type: String,
    default: 'default',
    validator: value => ['default', 'glass'].includes(value)
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
  },
  disable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

function isActive(value) {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.includes(value)
  }
  return props.modelValue === value
}

function select(value) {
  if (props.disable) return
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
@use '../../css/glass' as glass;

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
  padding: 15px;
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

.base-choice--glass .base-choice__option {
  @include glass.glass-light($raise-children: false);
  border-color: transparent;
  color: var(--dvijok-bg-dark);
}

.base-choice--glass .base-choice__option--active {
  background: var(--dvijok-choice-active);
  border-color: transparent;
  color: var(--dvijok-blue-primary);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
}

.base-choice--glass .base-choice__option:hover:not(.base-choice__option--active) {
  border-color: transparent;
  color: var(--dvijok-bg-dark);
}

.base-choice--disabled .base-choice__option:hover:not(.base-choice__option--active) {
  border-color: var(--dvijok-text-secondary);
  color: var(--dvijok-text-secondary);
}

.base-choice--glass.base-choice--disabled .base-choice__option:hover:not(.base-choice__option--active) {
  border-color: transparent;
  background: var(--dvijok-glass-tint);
  color: var(--dvijok-bg-dark);
}

.base-choice--disabled {
  pointer-events: none;
}

.base-choice--disabled .base-choice__option {
  cursor: default;
}
</style>
