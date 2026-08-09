<template>
  <div class="service-step">
    <BookingStepHead :name="branchName" :address="branchAddress" @back="emit('back')" />

    <h2 class="booking-step-title">Выбрать услугу</h2>

    <BaseSelect
      :model-value="modelValue"
      :options="options"
      placeholder="Выбрать услугу"
      block
      @update:model-value="emit('update:modelValue', $event)"
    />

    <BaseButton color="blue1" size="sm" block @click="emit('next')">Далее</BaseButton>
  </div>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BookingStepHead from '@/components/booking/BookingStepHead.vue'

defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  branchName: {
    type: String,
    default: ''
  },
  branchAddress: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'back', 'next'])
</script>

<style scoped lang="scss">
.service-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
