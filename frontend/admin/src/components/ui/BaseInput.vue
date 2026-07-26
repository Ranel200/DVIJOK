<template>
  <q-input
    :class="['base-input', { 'base-input--block': block }]"
    :model-value="modelValue"
    :type="type"
    :placeholder="placeholder"
    :disable="disable"
    :readonly="readonly"
    :rules="rules"
    :error="error"
    :error-message="errorMessage"
    :label="label"
    :for="inputId"
    :dense="dense"
    :mask="mask"
    :fill-mask="fillMask"
    :outlined="false"
    :borderless="true"
    no-error-icon
    hide-bottom-space
    @update:model-value="onUpdate"
  >
    <template v-if="$slots.prepend" #prepend>
      <slot name="prepend" />
    </template>
    <template v-if="$slots.append" #append>
      <slot name="append" />
    </template>
  </q-input>
</template>

<script setup>
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
  inputId: {
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
  },
  mask: {
    type: String,
    default: ''
  },
  fillMask: {
    type: [Boolean, String],
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

function onUpdate(value) {
  emit('update:modelValue', value)
}
</script>

<style scoped lang="scss">
.base-input {
  :deep(.q-field__control) {
    background-color: var(--dvijok-white);
    border: 1px solid var(--dvijok-text-secondary);
    border-radius: 10px;
    padding: 7px 14px;
    min-height: auto;
    height: auto;
  }

  :deep(.q-field__prepend),
  :deep(.q-field__append) {
    min-height: auto;
    height: auto;
    padding: 0;
  }

  :deep(.q-field__native) {
    color: var(--dvijok-bg-dark);
    font-size: 12px;
    line-height: 16px;
    padding: 0;

    &::placeholder {
      color: var(--dvijok-text-secondary);
    }
  }

  :deep(.q-field__control-container) {
    padding: 0;
    min-height: auto;
    height: auto;
  }

  :deep(.q-field__label) {
    color: var(--dvijok-text-secondary);
    font-size: 12px;
    line-height: 16px;
    top: 7px;
  }
}

.base-input--block {
  width: 100%;
}

.base-input.q-field--focused {
  :deep(.q-field__control) {
    border-color: var(--dvijok-bg-dark);
  }
}

.base-input.q-field--disabled,
.base-input.q-field--readonly {
  :deep(.q-field__control) {
    opacity: 0.6;
  }
}
</style>
