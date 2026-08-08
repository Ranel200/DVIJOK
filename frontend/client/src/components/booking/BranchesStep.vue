<template>
  <div class="branches-step">
    <h2 class="booking-step-title">Выберите филиал</h2>

    <AppBlock>
      <div class="branches-step__city">
        <img
          class="branches-step__city-icon"
          src="/client/icons/record/geo.svg"
          alt=""
          width="20"
          height="24"
        />
        <span class="branches-step__city-name">{{ city }}</span>
      </div>
    </AppBlock>

    <h2 class="booking-step-title">{{ title }}</h2>

    <AppBlock v-for="branch in branches" :key="branch.id" compact class="branches-step__branch">
      <img class="branches-step__map" :src="branch.mapSrc" alt="" />
      <BranchInfo
        :name="branch.name"
        :address="branch.address"
        :is-open="branch.isOpen"
        :until="branch.until"
      />
      <BaseButton color="blue1" size="sm" block @click="emit('select', branch)">Выбрать</BaseButton>
    </AppBlock>
  </div>
</template>

<script setup>
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BranchInfo from '@/components/booking/BranchInfo.vue'

defineProps({
  city: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  branches: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select'])
</script>

<style scoped lang="scss">
.branches-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.branches-step__city {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 9px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 6px;
  box-sizing: border-box;
}

.branches-step__city-icon {
  display: block;
  flex-shrink: 0;
}

.branches-step__city-name {
  font-weight: 700;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.branches-step__branch {
  gap: 15px;
}

.branches-step__map {
  display: block;
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 5px;
}
</style>
