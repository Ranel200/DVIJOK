<template>
  <AdminHeader :action="action" @action-click="onAction">
    <template #below>
      <SummaryCards :cards="cards" :loading="loading" />
      <div class="services-filters">
        <label class="services-filter services-filter--search">
          <img src="/admin/icons/search.svg" alt="" class="services-filter__icon" />
          <input
            v-model="search"
            type="text"
            class="services-filter__input"
            placeholder="Поиск по названию услуги"
          />
        </label>
        <div class="services-filter services-filter--choices">
          <BaseChoice
            v-model="choice"
            shape="pill"
            :options="choices"
            class="services-filter__choice"
          />
        </div>
      </div>
    </template>
  </AdminHeader>
  <div class="services"></div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import { servicesApi } from '@/api/index.js'
import { pluralize } from '@/utils/pluralize.js'

const action = { label: '+ Добавить услугу' }

const summary = ref(null)
const loading = ref(true)
const search = ref('')
const choice = ref('all')
const choices = [
  { label: 'Категория', value: 'category' },
  { label: 'Мастер', value: 'master' },
  { label: 'Цена', value: 'price' },
  { label: 'Все', value: 'all' }
]

const cardLayout = [
  {
    key: 'totalServices',
    title: 'Всего услуг',
    icon: '/admin/icons/services/gear.svg'
  },
  {
    key: 'averageCheck',
    title: 'Средний чек услуги',
    icon: '/admin/icons/services/ruble.svg'
  },
  {
    key: 'popularService',
    title: 'Популярная услуга',
    special: true,
    icon: '/admin/icons/services/star.svg'
  },
  {
    key: 'revenuePerMonth',
    title: 'Выручка за месяц',
    icon: '/admin/icons/services/stripes.svg'
  },
  {
    key: 'activeMasters',
    title: 'Активных мастеров',
    icon: '/admin/icons/services/man.svg'
  }
]

const cards = computed(() => {
  const s = summary.value
  return cardLayout.map(item => {
    if (item.special) {
      const popular = s?.popularService
      return {
        ...item,
        serviceTitle: popular?.name ?? '',
        value: popular
          ? `${popular.ordersPerMonth} ${pluralize(popular.ordersPerMonth, ['заказ', 'заказа', 'заказов'])} за месяц`
          : ''
      }
    }
    const raw = s ? s[item.key] : ''
    const value =
      item.key === 'averageCheck' || item.key === 'revenuePerMonth'
        ? formatRubles(raw)
        : String(raw ?? '')
    return { ...item, value }
  })
})

function formatRubles(value) {
  return `${formatNumber(value)} ₽`
}

function formatNumber(value) {
  return new Intl.NumberFormat('ru-RU').format(value)
}

function onAction() {
  // TODO: открыть форму добавления услуги
}

onMounted(async () => {
  try {
    summary.value = await servicesApi.summary()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.services-filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 16px;
}

.services-filter {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 11px 15px;
  box-sizing: border-box;
  border: 1px solid var(--dvijok-bg-dark);
  border-radius: 8px;
}

.services-filter--search {
  padding: 6px 10px;
  width: 265px;
}

.services-filter--choices {
  width: 45%;
  padding: 0;
  border: none;
}

.services-filter__choice {
  width: 100%;
}

.services-filter__icon {
  display: block;
  flex-shrink: 0;
}

.services-filter__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  color: var(--dvijok-bg-dark);
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;

  &::placeholder {
    color: var(--dvijok-bg-dark);
  }
}
</style>
