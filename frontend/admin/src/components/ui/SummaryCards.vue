<template>
  <div class="summary-cards">
    <template v-for="i in count" :key="i">
      <div v-if="cards[i - 1]" class="summary-cards__card">
        <div
          class="summary-cards__info"
          :class="{ 'summary-cards__info--special': cards[i - 1].special }"
        >
          <div class="summary-cards__title">{{ cards[i - 1].title }}</div>
          <template v-if="loading">
            <div v-if="cards[i - 1].special" class="summary-cards__special-block">
              <div
                class="summary-cards__skeleton-line summary-cards__skeleton-line--service-title"
              ></div>
              <div
                class="summary-cards__skeleton-line summary-cards__skeleton-line--sub-value"
              ></div>
            </div>
            <div
              v-else
              class="summary-cards__skeleton-line summary-cards__skeleton-line--value"
            ></div>
          </template>
          <template v-else>
            <div v-if="cards[i - 1].special" class="summary-cards__special-block">
              <div class="summary-cards__service-title">
                {{ cards[i - 1].serviceTitle }}
              </div>
              <div class="summary-cards__sub-value">{{ cards[i - 1].value }}</div>
            </div>
            <div v-else class="summary-cards__value">{{ cards[i - 1].value }}</div>
          </template>
        </div>
        <div v-if="cards[i - 1].icon" class="summary-cards__icon">
          <img :src="cards[i - 1].icon" alt="" />
        </div>
      </div>
      <div v-else class="summary-cards__card summary-cards__card--placeholder"></div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  cards: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  count: {
    type: Number,
    default: 5
  }
})
</script>

<style scoped lang="scss">
.summary-cards {
  display: flex;
  gap: 16px;
  width: 100%;
}

.summary-cards__card {
  display: flex;
  align-items: flex-start;
  flex: 1;
  min-width: 0;
  gap: 10px;
  padding: 10px 15px;
  background: var(--dvijok-white);
  border-radius: 6px;
  box-sizing: border-box;
}

.summary-cards__card--placeholder {
  background: transparent;
}

.summary-cards__info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  gap: 10px;
}

.summary-cards__info--special {
  gap: 5px;
}

.summary-cards__title {
  color: var(--dvijok-text-secondary);
  font-size: 12px;
  font-weight: 700;
  line-height: 15px;
}

.summary-cards__value {
  color: var(--dvijok-text-heading);
  font-size: 24px;
  font-weight: 700;
  line-height: 29px;
}

.summary-cards__special-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-cards__service-title {
  color: var(--dvijok-text-heading);
  font-size: 16px;
  font-weight: 700;
  line-height: 19px;
}

.summary-cards__sub-value {
  color: var(--dvijok-text-secondary);
  font-size: 10px;
  font-weight: 400;
  line-height: 12px;
}

.summary-cards__icon {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  line-height: 0;
}

.summary-cards__icon img {
  display: block;
  width: auto;
  height: 24px;
}

.summary-cards__skeleton-line {
  border-radius: 4px;
  background: var(--dvijok-muted);
  animation: summary-cards-skeleton-pulse 1.2s ease-in-out infinite;
}

.summary-cards__skeleton-line--value {
  width: 120px;
  height: 29px;
}

.summary-cards__skeleton-line--service-title {
  width: 100px;
  height: 19px;
}

.summary-cards__skeleton-line--sub-value {
  width: 140px;
  height: 12px;
}

@keyframes summary-cards-skeleton-pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}
</style>
