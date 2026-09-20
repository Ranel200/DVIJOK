<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="arrow-diag-icon"
    :class="[`arrow-diag-icon--${direction}`]"
    :style="iconStyle"
    aria-hidden="true"
  >
    <path
      d="M14 14L34 34M14 34H34V14"
      stroke="currentColor"
      stroke-width="4"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  direction: {
    type: String,
    default: 'down-right',
    validator: value => ['down-right', 'up-left'].includes(value)
  },
  color: {
    type: String,
    default: '#2E68FF'
  },
  size: {
    type: [Number, String],
    default: 48,
    validator: value => Number(value) > 0
  }
})

const iconStyle = computed(() => ({
  color: props.color
}))
</script>

<style scoped>
.arrow-diag-icon {
  display: block;
  flex-shrink: 0;
  transition:
    transform 0.3s ease,
    color 0.3s ease;
}

.arrow-diag-icon--down-right {
  transform: rotate(0deg);
}

.arrow-diag-icon--up-left {
  transform: rotate(180deg);
}
</style>
