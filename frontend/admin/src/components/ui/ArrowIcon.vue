<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="arrow-icon"
    :class="[`arrow-icon--${direction}`]"
    :style="iconStyle"
    aria-hidden="true"
  >
    <path
      d="M12.175 9L6.575 14.6L8 16L16 8L8 0L6.575 1.4L12.175 7H0V9H12.175Z"
      fill="currentColor"
    />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  direction: {
    type: String,
    default: 'right',
    validator: value => ['right', 'left'].includes(value)
  },
  color: {
    type: String,
    default: null
  },
  size: {
    type: [Number, String],
    default: 16
  }
})

const iconStyle = computed(() => {
  const style = {}
  if (props.color) {
    style.color = props.color
  }
  return style
})
</script>

<style scoped>
.arrow-icon {
  display: block;
}

.arrow-icon--left {
  transform: scaleX(-1);
}
</style>
