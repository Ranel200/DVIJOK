<template>
  <nav class="home-tabs" aria-label="Основная навигация">
    <button
      v-for="item in clientTabs"
      :key="item.name"
      type="button"
      class="home-tabs__item"
      :class="{ 'home-tabs__item--active': modelValue === item.name }"
      :aria-label="item.label"
      :aria-current="modelValue === item.name ? 'page' : undefined"
      @click="$emit('update:modelValue', item.name)"
    >
      <span class="home-tabs__content">
        <component :is="icons[item.icon]" class="home-tabs__icon" />
        <span class="home-tabs__caption">
          <span class="home-tabs__label">{{ item.label }}</span>
          <span class="home-tabs__underline" aria-hidden="true" />
        </span>
      </span>
    </button>
  </nav>
</template>

<script setup>
import { clientTabs } from '@/constants/navigation.js'
import CarIcon from '@/components/icons/CarIcon.vue'
import HistoryIcon from '@/components/icons/HistoryIcon.vue'
import RecordIcon from '@/components/icons/RecordIcon.vue'

defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

defineEmits(['update:modelValue'])

const icons = {
  car: CarIcon,
  history: HistoryIcon,
  record: RecordIcon
}
</script>

<style scoped lang="scss">
.home-tabs {
  display: flex;
  flex-shrink: 0;
  justify-content: space-between;
  align-items: flex-start;
  gap: 5px;
  padding: 20px 30px;
  background: var(--dvijok-gradient-brand);
}

.home-tabs__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--dvijok-tab-inactive);
  cursor: pointer;
  appearance: none;
  -webkit-tap-highlight-color: transparent;

  &--active {
    color: var(--dvijok-white);
  }
}

.home-tabs__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.home-tabs__caption {
  display: flex;
  flex-direction: column;
  width: max-content;
  gap: 9px;
}

.home-tabs__label {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  white-space: nowrap;
}

.home-tabs__underline {
  width: 100%;
  height: 2px;
  background: transparent;
}

.home-tabs__item--active .home-tabs__underline {
  background: var(--dvijok-white);
}
</style>
