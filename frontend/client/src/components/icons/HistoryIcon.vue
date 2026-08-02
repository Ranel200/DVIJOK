<template>
  <svg
    :width="width"
    :height="height"
    viewBox="0 0 34 33"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="history-icon"
    :style="color ? { color } : undefined"
    aria-hidden="true"
  >
    <path
      d="M5.66927 27.5C4.8901 27.5 4.22309 27.2307 3.66823 26.6922C3.11337 26.1536 2.83594 25.5063 2.83594 24.75V8.25C2.83594 7.49375 3.11337 6.84635 3.66823 6.30781C4.22309 5.76927 4.8901 5.5 5.66927 5.5H14.1693L17.0026 8.25H28.3359C29.1151 8.25 29.7821 8.51927 30.337 9.05781C30.8918 9.59635 31.1693 10.2438 31.1693 11V24.75C31.1693 25.5063 30.8918 26.1536 30.337 26.6922C29.7821 27.2307 29.1151 27.5 28.3359 27.5H5.66927ZM5.66927 24.75H28.3359V11H15.8339L13.0005 8.25H5.66927V24.75Z"
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
  width: {
    type: [Number, String],
    default: 34
  },
  height: {
    type: [Number, String],
    default: 33
  }
})
</script>

<style scoped>
.history-icon {
  display: block;
  flex-shrink: 0;
}
</style>
