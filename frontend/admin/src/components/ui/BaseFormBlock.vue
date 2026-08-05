<template>
  <section
    :class="[
      'base-form-block',
      {
        'base-form-block--horizontal': layout === 'horizontal',
        'base-form-block--stack': stackFields
      }
    ]"
  >
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
  },
  layout: {
    type: String,
    default: 'vertical',
    validator: value => ['vertical', 'horizontal'].includes(value)
  },
  stackFields: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped lang="scss">
.base-form-block {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.base-form-block--horizontal {
  gap: 20px;
}

.base-form-block__title {
  margin: 0;
  color: var(--dvijok-form-block-title, var(--dvijok-bg-dark));
  font-size: 16px;
  font-weight: 700;
  line-height: 19px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.base-form-block__fields {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.base-form-block--horizontal .base-form-block__fields {
  display: grid;
  grid-template-columns: max-content 1fr;
  column-gap: 15px;
  row-gap: 10px;
  align-items: center;
}

.base-form-block--horizontal.base-form-block--stack .base-form-block__fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
