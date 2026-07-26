<template>
  <svg
    :width="size"
    :height="height"
    viewBox="0 0 10 5"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="chevron-icon"
    :class="[`chevron-icon--${direction}`]"
    :style="iconStyle"
    aria-hidden="true"
  >
    <path d="M5 5L0 0H10L5 5Z" fill="currentColor" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  direction: {
    type: String,
    default: 'down',
    validator: value => ['up', 'down'].includes(value)
  },
  color: {
    type: String,
    default: null
  },
  size: {
    type: [Number, String],
    default: 10
  }
})

const height = computed(() => Number(props.size) / 2)

const iconStyle = computed(() => {
  const style = {}
  if (props.color) {
    style.color = props.color
  }
  return style
})
</script>

<style scoped>
.chevron-icon {
  display: block;
  color: var(--dvijok-text-secondary);
}

.chevron-icon--up {
  transform: scaleY(-1);
}
</style>
