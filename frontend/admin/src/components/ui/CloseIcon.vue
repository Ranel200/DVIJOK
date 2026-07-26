<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 22 22"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="close-icon"
    :style="color ? { color } : undefined"
    aria-hidden="true"
  >
    <path
      d="M2.2 22L0 19.8L8.8 11L0 2.2L2.2 0L11 8.8L19.8 0L22 2.2L13.2 11L22 19.8L19.8 22L11 13.2L2.2 22Z"
      fill="currentColor"
    />
  </svg>
</template>

<script setup>
defineProps({
  color: {
    type: String,
    default: ''
  },
  size: {
    type: [Number, String],
    default: 22
  }
})
</script>

<style scoped>
.close-icon {
  display: block;
  color: var(--dvijok-bg-dark);
}
</style>
