<template>
  <AppBlock class="history-card">
    <div class="history-card__head">
      <div class="history-card__title-row">
        <h3 class="history-card__title">{{ title }}</h3>
        <span class="history-card__badge" :class="`history-card__badge--${status}`">
          {{ statusLabel }}
        </span>
      </div>
      <p class="history-card__car">{{ carLabel }}</p>
    </div>

    <div class="history-card__fields">
      <div class="history-card__field">
        <span class="history-card__label">Автосервис</span>
        <span class="history-card__service">“{{ serviceName }}”</span>
        <span class="history-card__address">{{ serviceAddress }}</span>
      </div>

      <div class="history-card__field">
        <span class="history-card__label">Мастер</span>
        <span class="history-card__value">{{ master }}</span>
      </div>

      <div class="history-card__field">
        <span class="history-card__label">Дата</span>
        <span class="history-card__value">{{ datetime }}</span>
      </div>
    </div>

    <div class="history-card__footer">
      <div class="history-card__amount">
        <span class="history-card__label">Сумма за работу</span>
        <span class="history-card__price">{{ amountLabel }}</span>
      </div>

      <button
        type="button"
        class="history-card__order"
        :style="{ color: orderColor, borderColor: orderColor }"
        :aria-label="`Заказ-наряд №${orderNumber}`"
        @click="emit('open-order')"
      >
        <PdfIcon :color="orderColor" :width="24" :height="24" />
        <span class="history-card__order-text">
          <span class="history-card__order-title">Заказ-наряд №{{ orderNumber }}</span>
          <span class="history-card__order-status">Статус: {{ orderStatusLabel }}</span>
        </span>
      </button>
    </div>
  </AppBlock>
</template>

<script setup>
import { computed } from 'vue'
import AppBlock from '@/components/ui/AppBlock.vue'
import PdfIcon from '@/components/icons/PdfIcon.vue'

const STATUS_LABELS = {
  new: 'Новая запись',
  in_progress: 'В работе',
  approval: 'Согласование',
  completed: 'Завершено'
}

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    validator: value => ['new', 'in_progress', 'approval', 'completed'].includes(value)
  },
  carBrand: {
    type: String,
    required: true
  },
  carPlate: {
    type: String,
    required: true
  },
  serviceName: {
    type: String,
    required: true
  },
  serviceAddress: {
    type: String,
    required: true
  },
  master: {
    type: String,
    required: true
  },
  datetime: {
    type: String,
    required: true
  },
  amount: {
    type: Number,
    required: true
  },
  orderNumber: {
    type: String,
    required: true
  },
  orderReady: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['open-order'])

const statusLabel = computed(() => STATUS_LABELS[props.status] || props.status)

const carLabel = computed(() => `${props.carBrand} · ${props.carPlate}`)

const amountLabel = computed(() => {
  const formatted = Math.round(props.amount)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return `${formatted} ₽`
})

const orderColor = computed(() =>
  props.orderReady ? 'var(--dvijok-blue-primary)' : 'var(--dvijok-text-secondary)'
)

const orderStatusLabel = computed(() => (props.orderReady ? 'Готов' : 'Еще не готов'))
</script>

<style scoped lang="scss">
.history-card {
  gap: 20px;
}

.history-card__head {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.history-card__title-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.history-card__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.history-card__badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 50px;
  font-weight: 500;
  font-size: 10px;
  line-height: normal;
  white-space: nowrap;
}

.history-card__badge--new {
  background: #b3c8ff;
  color: #093095;
}

.history-card__badge--in_progress {
  background: #ffccae;
  color: #d45813;
}

.history-card__badge--approval {
  background: #efcdff;
  color: #9d1fdb;
}

.history-card__badge--completed {
  background: #ceffa3;
  color: #2f8527;
}

.history-card__car {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: normal;
  color: var(--dvijok-text-secondary);
}

.history-card__fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-card__field {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.history-card__label {
  font-weight: 400;
  font-size: 13px;
  line-height: normal;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.history-card__service {
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.history-card__address {
  font-weight: 400;
  font-size: 11px;
  line-height: normal;
  color: var(--dvijok-text-secondary);
}

.history-card__value {
  font-weight: 400;
  font-size: 13px;
  line-height: normal;
  color: var(--dvijok-bg-dark);
}

.history-card__footer {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.history-card__amount {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.history-card__price {
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.history-card__order {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
  margin: 0;
  padding: 5px 7px;
  border: 1px solid;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.history-card__order-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.history-card__order-title {
  font-weight: 700;
  font-size: 11px;
  line-height: 17px;
}

.history-card__order-status {
  font-weight: 400;
  font-size: 10px;
  line-height: normal;
}
</style>
