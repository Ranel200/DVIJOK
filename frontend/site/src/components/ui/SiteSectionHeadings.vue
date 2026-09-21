<template>
  <div class="section-headings">
    <p class="section-headings__eyebrow">{{ eyebrow }}</p>
    <h2 class="section-headings__title">{{ title }}</h2>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.section-headings {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.section-headings__eyebrow {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-transform: uppercase;
  color: var(--dvijok-blue-bright);
}

.section-headings__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 48px;
  text-transform: uppercase;
  color: #000;
}
</style>
