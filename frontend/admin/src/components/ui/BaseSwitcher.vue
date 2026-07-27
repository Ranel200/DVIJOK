<template>
  <button
    type="button"
    class="base-switcher"
    :class="{
      'base-switcher--active': modelValue,
      'base-switcher--disabled': disable
    }"
    role="switch"
    :aria-checked="modelValue"
    :aria-disabled="disable || undefined"
    :aria-label="ariaLabel"
    :tabindex="disable ? -1 : undefined"
    @click="toggle"
  >
    <span class="base-switcher__track" aria-hidden="true">
      <span class="base-switcher__knob" />
    </span>
    <span class="base-switcher__label" aria-hidden="true">
      <span class="base-switcher__label-text">{{ onLabel }}</span>
      <span class="base-switcher__label-text">{{ offLabel }}</span>
    </span>
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  disable: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: 'Переключатель'
  },
  onLabel: {
    type: String,
    default: 'Вкл'
  },
  offLabel: {
    type: String,
    default: 'Выкл'
  }
})

const emit = defineEmits(['update:modelValue'])

function toggle() {
  if (props.disable) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped lang="scss">
.base-switcher {
  display: inline-flex;
  align-items: center;
  gap: 15px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--dvijok-text-secondary);
}

.base-switcher__track {
  display: flex;
  align-items: center;
  box-sizing: border-box;
  width: 52px;
  padding: 3px 4px;
  border-radius: 50px;
  background: var(--dvijok-text-secondary);
  transition: background 0.18s ease;
}

.base-switcher__knob {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #c0caf2;
  transition:
    transform 0.18s ease,
    background 0.18s ease;
}

.base-switcher__label {
  display: grid;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: inherit;
}

.base-switcher__label-text {
  grid-area: 1 / 1;
  justify-self: start;
}

.base-switcher__label-text:first-child {
  visibility: hidden;
}

.base-switcher--active {
  color: var(--dvijok-success);
}

.base-switcher--active .base-switcher__label-text:first-child {
  visibility: visible;
}

.base-switcher--active .base-switcher__label-text:last-child {
  visibility: hidden;
}

.base-switcher--active .base-switcher__track {
  background: var(--dvijok-success);
}

.base-switcher--active .base-switcher__knob {
  background: var(--dvijok-success-bg);
  transform: translateX(28px);
}

.base-switcher--disabled {
  cursor: default;
  pointer-events: none;
}
</style>
