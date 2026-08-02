<template>
  <svg
    :width="size"
    :height="size"
    :viewBox="viewBox"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="arrow-icon"
    :class="[`arrow-icon--${direction}`]"
    :style="iconStyle"
    aria-hidden="true"
  >
    <path :d="path" fill="currentColor" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  direction: {
    type: String,
    default: 'right',
    validator: value => ['right', 'left', 'up', 'down'].includes(value)
  },
  color: {
    type: String,
    default: null
  },
  size: {
    type: [Number, String],
    default: 16,
    validator: value => Number(value) > 0
  }
})

const PATHS = {
  16: 'M12.175 9L6.575 14.6L8 16L16 8L8 0L6.575 1.4L12.175 7H0V9H12.175Z',
  14: 'M9.43509 7.58301H2.33301V6.41634H9.43509L6.16842 3.14967L6.99967 2.33301L11.6663 6.99967L6.99967 11.6663L6.16842 10.8497L9.43509 7.58301Z'
}

const BASE_SIZE = 16

const path = computed(() => PATHS[Number(props.size)] ?? PATHS[BASE_SIZE])
const viewBox = computed(() => {
  const size = Number(props.size)
  const base = PATHS[size] ? size : BASE_SIZE
  return `0 0 ${base} ${base}`
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

.arrow-icon--up {
  transform: rotate(-90deg);
}

.arrow-icon--down {
  transform: rotate(90deg);
}
</style>
