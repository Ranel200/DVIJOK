<template>
  <div
    :class="[
      'base-field',
      {
        'base-field--block': block,
        'base-field--horizontal': layout === 'horizontal',
        'base-field--textarea': type === 'textarea'
      }
    ]"
  >
    <label v-if="label" :for="readonly || disable ? undefined : fieldId" class="base-field__label">
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
        :mask="mask"
        :fill-mask="fillMask"
        :autogrow="type === 'textarea' ? autogrow : false"
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
  layout: {
    type: String,
    default: 'vertical',
    validator: value => ['vertical', 'horizontal'].includes(value)
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
  },
  mask: {
    type: String,
    default: ''
  },
  fillMask: {
    type: [Boolean, String],
    default: false
  },
  autogrow: {
    type: Boolean,
    default: true
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

.base-field--horizontal {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.base-field--horizontal.base-field--textarea {
  align-items: start;
}

.base-field__label {
  color: var(--dvijok-form-label, var(--dvijok-bg-dark));
  font-size: 16px;
  line-height: 19px;
  text-align: left;
  white-space: nowrap;
}

.base-field--horizontal .base-field__label {
  grid-column: 1;
}

.base-field--horizontal .base-field__control {
  grid-column: 2;
}

.base-field__control {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
  min-width: 0;
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
