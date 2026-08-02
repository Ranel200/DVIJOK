<template>
  <q-input
    :class="['base-input', { 'base-input--block': block, 'base-input--readonly': readonly }]"
    :model-value="modelValue"
    :type="type"
    :placeholder="placeholder"
    :disable="disable"
    :readonly="readonly"
    :input-attrs="mergedAttrs"
    :rules="rules"
    :error="error"
    :error-message="errorMessage"
    :for="inputId"
    :dense="dense"
    :mask="mask"
    :fill-mask="fillMask"
    :maxlength="maxlength"
    :autogrow="autogrow"
    :outlined="false"
    :borderless="true"
    no-error-icon
    hide-bottom-space
    @update:model-value="onUpdate"
    @focus="onFocus"
    @mousedown="onMouseDown"
    @keydown="onKeydown"
    @paste="onPaste"
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
import { computed } from 'vue'

const props = defineProps({
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
  },
  maxlength: {
    type: [Number, String],
    default: undefined
  },
  inputAttrs: {
    type: Object,
    default: () => ({})
  },
  autogrow: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'keydown', 'paste'])

const mergedAttrs = computed(() => {
  const locked = props.readonly || props.disable ? { tabindex: -1, readonly: true } : {}
  return { ...props.inputAttrs, ...locked }
})

function onUpdate(value) {
  emit('update:modelValue', value)
}

function onFocus(event) {
  if (!props.readonly) return
  event?.target?.blur?.()
}

function onMouseDown(event) {
  if (!props.readonly) return
  event.preventDefault()
}

function onKeydown(event) {
  emit('keydown', event)
}

function onPaste(event) {
  emit('paste', event)
}
</script>

<style scoped lang="scss">
.base-input {
  :deep(.q-field__control) {
    background-color: var(--dvijok-white);
    border: 1px solid var(--dvijok-text-secondary);
    border-radius: 6px;
    padding: 5px 9px;
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
    font-weight: 400;
    font-size: 13px;
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
}

.base-input--block {
  width: 100%;
}

.base-input {
  :deep(textarea.q-field__native) {
    min-height: 72px;
    resize: vertical;
  }
}

.base-input.q-field--focused {
  :deep(.q-field__control) {
    border-color: var(--dvijok-bg-dark);
  }
}

.base-input.q-field--disabled {
  :deep(.q-field__control) {
    opacity: 0.6;
  }
}

.base-input.q-field--readonly,
.base-input--readonly {
  pointer-events: none;

  :deep(.q-field__control),
  :deep(.q-field__native) {
    cursor: default;
    caret-color: transparent;
    pointer-events: none;
    user-select: none;
  }
}

.base-input.q-field--readonly.q-field--focused,
.base-input--readonly.q-field--focused {
  :deep(.q-field__control) {
    border-color: var(--dvijok-text-secondary);
  }
}
</style>
