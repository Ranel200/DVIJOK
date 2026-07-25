<template>
  <div :class="['base-choice', `base-choice--${shape}`]">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      :class="['base-choice__option', { 'base-choice__option--active': isActive(option.value) }]"
      :aria-pressed="isActive(option.value)"
      @click="select(option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Number],
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
  }
})

const emit = defineEmits(['update:modelValue'])

function isActive(value) {
  return props.modelValue === value
}

function select(value) {
  emit('update:modelValue', value)
}
</script>

<style scoped lang="scss">
.base-choice {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 17px;
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
  padding: 10px 25px;
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
