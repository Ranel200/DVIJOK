<template>
  <p v-if="message" class="base-form-error">{{ message }}</p>
</template>

<script setup>
import { useFormField } from '@/composables/useFormValidation.js'

const props = defineProps({
  validate: {
    type: Function,
    required: true
  }
})

const message = useFormField(() => {
  const result = props.validate()
  if (typeof result === 'string' && result) return result
  if (result === false) return 'Заполните поле'
  return ''
})
</script>

<style scoped lang="scss">
.base-form-error {
  margin: 0;
  color: var(--dvijok-danger, #c10015);
  font-size: 12px;
  line-height: 15px;
}
</style>
