<template>
  <div :class="['base-field', { 'base-field--block': block }]">
    <label v-if="label" :for="fieldId" class="base-field__label">
      {{ label }}
    </label>
    <div class="base-field__control">
      <BaseInput
        :input-id="fieldId"
        :class="['base-field__input']"
        :model-value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disable="disable"
        :readonly="readonly"
        :block="block"
        :dense="dense"
        :error="error"
        :error-message="errorMessage"
        :rules="rules"
        @update:model-value="onUpdate"
      >
        <template v-if="$slots.prepend" #prepend>
          <slot name="prepend" />
        </template>
        <template v-if="$slots.append" #append>
          <slot name="append" />
        </template>
      </BaseInput>
      <p v-if="hint" class="base-field__hint">{{ hint }}</p>
    </div>
  </div>
</template>

<script setup>
import { useId } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'

defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  disable: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  },
  dense: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  },
  rules: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const fieldId = useId()

function onUpdate(value) {
  emit('update:modelValue', value)
}
</script>

<style scoped lang="scss">
.base-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.base-field--block {
  width: 100%;
}

.base-field__label {
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  line-height: 16px;
  text-align: left;
}

.base-field__control {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
}

.base-field__input {
  width: 100%;
}

.base-field__hint {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}
</style>
