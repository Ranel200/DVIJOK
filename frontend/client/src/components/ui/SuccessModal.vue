<template>
  <BaseModal
    :model-value="modelValue"
    persistent
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="success-modal">
      <p class="success-modal__title">{{ title }}</p>
      <p v-if="note" class="success-modal__note">{{ note }}</p>
    </div>

    <BaseButton color="blue2" size="sm" block @click="emit('continue')"> Перейти </BaseButton>
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
  title: {
    type: String,
    default: ''
  },
  note: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'continue'])
</script>

<style scoped lang="scss">
.success-modal {
  display: flex;
  flex-direction: column;
  gap: 17px;
  width: 100%;
  text-align: center;
}

.success-modal__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.success-modal__note {
  margin: 0;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}
</style>
