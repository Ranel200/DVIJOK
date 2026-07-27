<template>
  <BaseModal
    :model-value="modelValue"
    :persistent="persistent"
    @update:model-value="emit('update:modelValue', $event)"
    @close="emit('close')"
  >
    <div class="success-modal">
      <h2 class="success-modal__title">{{ message }}</h2>
      <BaseButton color="blue1" size="lg" @click="onConfirm">
        {{ buttonLabel }}
      </BaseButton>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  buttonLabel: {
    type: String,
    default: 'Ок'
  },
  persistent: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'close'])

function onConfirm() {
  emit('update:modelValue', false)
  emit('confirm')
}
</script>

<style scoped lang="scss">
.success-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.success-modal__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}
</style>
