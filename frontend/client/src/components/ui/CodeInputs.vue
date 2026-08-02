<template>
  <div class="code-inputs" role="group" :aria-label="ariaLabel">
    <BaseInput
      v-for="(_, index) in digits"
      :key="index"
      :ref="el => setInputRef(el, index)"
      :model-value="digits[index]"
      class="code-inputs__cell"
      :maxlength="1"
      :input-attrs="{ inputmode: 'numeric', autocomplete: 'one-time-code' }"
      @update:model-value="value => onDigit(index, value)"
      @keydown="event => onKeydown(index, event)"
      @paste="onPaste"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  length: {
    type: Number,
    default: 4
  },
  ariaLabel: {
    type: String,
    default: 'Код подтверждения'
  }
})

const emit = defineEmits(['update:modelValue'])

const digits = ref(Array.from({ length: props.length }, (_, i) => props.modelValue[i] || ''))
const inputRefs = ref([])

watch(
  () => props.modelValue,
  value => {
    const next = Array.from({ length: props.length }, (_, i) => value[i] || '')
    if (next.join('') === digits.value.join('')) return
    digits.value = next
  }
)

function setInputRef(el, index) {
  inputRefs.value[index] = el
}

function focusAt(index) {
  const field = inputRefs.value[index]
  const native = field?.$el?.querySelector?.('input')
  native?.focus?.()
  native?.select?.()
}

function emitValue() {
  emit('update:modelValue', digits.value.join(''))
}

function onDigit(index, raw) {
  const char = String(raw ?? '')
    .replace(/\D/g, '')
    .slice(-1)
  digits.value[index] = char
  emitValue()
  if (char && index < props.length - 1) focusAt(index + 1)
}

function onKeydown(index, event) {
  if (event.key !== 'Backspace') return
  if (digits.value[index]) return
  if (index === 0) return
  event.preventDefault()
  digits.value[index - 1] = ''
  emitValue()
  focusAt(index - 1)
}

function onPaste(event) {
  const text = event.clipboardData?.getData('text') || ''
  const chars = text.replace(/\D/g, '').slice(0, props.length)
  if (!chars) return
  event.preventDefault()
  digits.value = Array.from({ length: props.length }, (_, i) => chars[i] || '')
  emitValue()
  focusAt(Math.min(chars.length, props.length - 1))
}
</script>

<style scoped lang="scss">
.code-inputs {
  display: flex;
  gap: 5px;
}

.code-inputs__cell {
  width: fit-content;
  flex: 0 0 auto;

  :deep(.q-field__control) {
    width: fit-content;
  }

  :deep(.q-field__control-container) {
    width: auto;
    flex: none;
  }

  :deep(.q-field__native) {
    width: 1ch;
    text-align: center;
  }
}
</style>
