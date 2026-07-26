<template>
  <header class="admin-header" :style="{ gap: gapValue }">
    <div class="admin-header__row admin-header__row--title">
      <div class="admin-header__title-group">
        <slot name="leading" />
        <h1 class="admin-header__title">{{ title }}</h1>
        <div v-if="$slots['title-trailing']" class="admin-header__title-trailing">
          <slot name="title-trailing" />
        </div>
      </div>
      <div v-if="$slots.trailing || action" class="admin-header__actions">
        <slot name="trailing" />
        <BaseButton
          v-if="action"
          color="blue1"
          size="lg"
          class="admin-header__action"
          @click="$emit('action-click', $event)"
        >
          <template v-if="$slots['action-icon']" #prepend>
            <slot name="action-icon" />
          </template>
          {{ action.label }}
        </BaseButton>
      </div>
    </div>

    <div v-if="tabs.length" class="admin-header__row admin-header__row--tabs">
      <BaseTabs
        :model-value="activeTab"
        :options="tabs"
        @update:model-value="$emit('update:active-tab', $event)"
      />
    </div>

    <slot name="below" />
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseTabs from '@/components/ui/BaseTabs.vue'

const props = defineProps({
  title: {
    type: String,
    default: null
  },
  tabs: {
    type: Array,
    default: () => []
  },
  activeTab: {
    type: [String, Number],
    default: ''
  },
  action: {
    type: Object,
    default: null
  },
  gap: {
    type: [String, Number],
    default: '30px'
  }
})

defineEmits(['update:active-tab', 'action-click'])

const route = useRoute()

const title = computed(() => props.title || route.meta.title || 'DVIJOK Admin')
const gapValue = computed(() => {
  const g = props.gap
  if (g === undefined || g === null) return '30px'
  return typeof g === 'number' ? `${g}px` : g
})
</script>

<style scoped lang="scss">
.admin-header {
  display: flex;
  flex-direction: column;
  padding: 40px 20px 30px;
}

.admin-header__row {
  display: flex;
  width: 100%;
}

.admin-header__row--title {
  align-items: center;
  justify-content: space-between;
}

.admin-header__title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-header__title-trailing {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-left: 18px;
}

.admin-header__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-header__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 700;
  line-height: 36px;
}
</style>
