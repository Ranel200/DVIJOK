<template>
  <header class="page-intro">
    <h1 class="page-intro__title">{{ title }}</h1>
    <div class="page-intro__divider" aria-hidden="true" />
    <p class="page-intro__lead">{{ lead }}</p>
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  lead: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.page-intro {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.page-intro__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-align: center;
  text-transform: uppercase;
  color: #000;
}

.page-intro__divider {
  width: 100%;
  height: 3px;
  background: #2e68ff;
}

.page-intro__lead {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-align: center;
  color: #000;
}
</style>
