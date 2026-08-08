<template>
  <div class="branch-info">
    <p class="branch-info__name">{{ name }}</p>
    <p class="branch-info__address">{{ address }}</p>
    <p
      class="branch-info__hours"
      :class="isOpen ? 'branch-info__hours--open' : 'branch-info__hours--closed'"
    >
      {{ hoursText }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { hoursLabel } from '@/utils/booking.js'

const props = defineProps({
  name: {
    type: String,
    default: ''
  },
  address: {
    type: String,
    default: ''
  },
  isOpen: {
    type: Boolean,
    default: false
  },
  until: {
    type: String,
    default: ''
  }
})

const hoursText = computed(() => hoursLabel({ isOpen: props.isOpen, until: props.until }))
</script>

<style scoped lang="scss">
.branch-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.branch-info__name {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.branch-info__address {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}

.branch-info__hours {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
}

.branch-info__hours--open {
  color: var(--dvijok-workday);
}

.branch-info__hours--closed {
  color: var(--dvijok-danger);
}
</style>
