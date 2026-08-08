<template>
  <div class="booking-step-head">
    <button type="button" class="booking-step-head__back" aria-label="Назад" @click="emit('back')">
      <ArrowIcon direction="left" :size="16" color="var(--dvijok-blue-primary)" />
    </button>
    <div class="booking-step-head__summary">
      <div class="booking-step-head__avatar" aria-hidden="true" />
      <div class="booking-step-head__text">
        <p class="booking-step-head__name">{{ name }}</p>
        <p class="booking-step-head__address">{{ address }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import ArrowIcon from '@/components/ui/ArrowIcon.vue'

defineProps({
  name: {
    type: String,
    default: ''
  },
  address: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['back'])
</script>

<style scoped lang="scss">
.booking-step-head {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
}

.booking-step-head__back {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.booking-step-head__summary {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.booking-step-head__avatar {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--dvijok-accent-cyan);
}

.booking-step-head__text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
  min-width: 0;
}

.booking-step-head__name {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.booking-step-head__address {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}
</style>
