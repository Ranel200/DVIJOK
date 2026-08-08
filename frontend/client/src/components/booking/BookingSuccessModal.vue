<template>
  <BaseModal
    :model-value="modelValue"
    persistent
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="booking-success">
      <p class="booking-success__title">Вы успешно записаны!</p>
      <p class="booking-success__note">
        Войдите в личный кабинет сервиса
        <span class="booking-success__brand">“ДВИЖОК”</span>
      </p>
    </div>

    <div class="booking-success__actions">
      <BaseButton color="green" size="sm" block @click="emit('cabinet')">
        Перейти в личный кабинет
      </BaseButton>
      <BaseButton color="blue2" size="sm" class="booking-success__exit" @click="emit('exit')">
        Выйти
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
  }
})

const emit = defineEmits(['update:modelValue', 'cabinet', 'exit'])
</script>

<style scoped lang="scss">
.booking-success {
  display: flex;
  flex-direction: column;
  gap: 17px;
  width: 100%;
  text-align: center;
}

.booking-success__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-success__note {
  margin: 0;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-success__brand {
  font-weight: 700;
}

.booking-success__actions {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 20px;
  width: 100%;
}

.booking-success__exit {
  align-self: flex-start;
  width: fit-content;
}
</style>
