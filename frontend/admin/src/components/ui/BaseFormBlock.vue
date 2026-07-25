<template>
  <section class="base-form-block">
    <h2 v-if="title" class="base-form-block__title">{{ title }}</h2>
    <div class="base-form-block__fields">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  }
})
</script>

<style scoped lang="scss">
.base-form-block {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.base-form-block__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  font-weight: 700;
  line-height: 17px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.base-form-block__fields {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
