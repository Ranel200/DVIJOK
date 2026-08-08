<template>
  <div class="menu-step">
    <h2 class="booking-step-title">Записаться</h2>

    <AppBlock v-if="branch" compact class="menu-step__branch">
      <div class="menu-step__photo-stub" aria-hidden="true" />
      <BranchInfo
        :name="branch.name"
        :address="branch.address"
        :is-open="branch.isOpen"
        :until="branch.until"
      />
    </AppBlock>

    <div class="menu-step__list">
      <GlassActionRow
        v-for="item in items"
        :key="item.id"
        :icon="item.icon"
        :label="item.label"
        @click="emit('navigate', item.id)"
      />
    </div>
  </div>
</template>

<script setup>
import AppBlock from '@/components/ui/AppBlock.vue'
import BranchInfo from '@/components/booking/BranchInfo.vue'
import GlassActionRow from '@/components/booking/GlassActionRow.vue'

defineProps({
  branch: {
    type: Object,
    default: null
  },
  items: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['navigate'])
</script>

<style scoped lang="scss">
.menu-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.menu-step__branch {
  gap: 15px;
}

.menu-step__photo-stub {
  width: 100%;
  height: 192px;
  border-radius: 5px;
  background: var(--dvijok-text-secondary);
}

.menu-step__list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
