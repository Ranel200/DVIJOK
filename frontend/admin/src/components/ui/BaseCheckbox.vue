<template>
  <label :class="['base-checkbox', { 'base-checkbox--disabled': disable }]">
    <input
      type="checkbox"
      class="base-checkbox__input"
      :checked="modelValue"
      :disabled="disable"
      @change="onChange"
    />
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 19 19"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="base-checkbox__box"
      aria-hidden="true"
    >
      <path :d="boxPath" fill="currentColor" />
      <path v-if="modelValue" :d="checkPath" fill="currentColor" />
    </svg>
    <span v-if="label" class="base-checkbox__label">{{ label }}</span>
  </label>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  },
  size: {
    type: [Number, String],
    default: 19
  },
  disable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const boxPath =
  'M3.95833 16.625C3.52292 16.625 3.15017 16.47 2.8401 16.1599C2.53003 15.8498 2.375 15.4771 2.375 15.0417V3.95833C2.375 3.52292 2.53003 3.15017 2.8401 2.8401C3.15017 2.53003 3.52292 2.375 3.95833 2.375H15.0417C15.4771 2.375 15.8498 2.53003 16.1599 2.8401C16.47 3.15017 16.625 3.52292 16.625 3.95833V15.0417C16.625 15.4771 16.47 15.8498 16.1599 16.1599C15.8498 16.47 15.4771 16.625 15.0417 16.625H3.95833ZM3.95833 15.0417H15.0417V3.95833H3.95833V15.0417Z'

const checkPath =
  'M8.39167 12.825L13.9729 7.24375L12.8646 6.13542L8.39167 10.6083L6.13542 8.35208L5.02708 9.46042L8.39167 12.825Z'

function onChange(event) {
  emit('update:modelValue', event.target.checked)
}
</script>

<style scoped lang="scss">
.base-checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.base-checkbox__input {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: 0;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

.base-checkbox__box {
  display: block;
  flex-shrink: 0;
  color: var(--dvijok-link);
}

.base-checkbox__label {
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  line-height: 16px;
  text-align: left;
}

.base-checkbox--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
