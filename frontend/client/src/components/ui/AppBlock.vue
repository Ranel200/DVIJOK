<template>
  <div
    class="app-block"
    :class="[
      `app-block--${variant}`,
      {
        'app-block--fixed': fixedHeight,
        'app-block--compact': compact,
        'app-block--active': active
      }
    ]"
  >
    <div v-if="title || subtitle" class="app-block__head">
      <h2 v-if="title" class="app-block__title">{{ title }}</h2>
      <p v-if="subtitle" class="app-block__subtitle">{{ subtitle }}</p>
    </div>

    <slot />
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'white',
    validator: value => ['white', 'dark'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  fixedHeight: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped lang="scss">
.app-block {
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-radius: 10px;
  padding: 20px 30px;
}

.app-block--compact {
  gap: 15px;
  padding: 12px 10px;
}

.app-block--active {
  padding: 19px 29px;
  border: 1px solid var(--dvijok-blue-primary);
}

.app-block--compact.app-block--active {
  padding: 11px 9px;
}

.app-block--white {
  background: var(--dvijok-white);
}

.app-block--dark {
  background: var(--dvijok-gradient-brand);
}

.app-block--fixed {
  height: 200px;
}

.app-block__head {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.app-block__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
}

.app-block--white .app-block__title {
  color: var(--dvijok-text-primary);
}

.app-block--white.app-block--active .app-block__title {
  color: var(--dvijok-blue-primary);
}

.app-block--dark .app-block__title {
  color: var(--dvijok-white);
}

.app-block__subtitle {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
  white-space: pre-line;
}
</style>
