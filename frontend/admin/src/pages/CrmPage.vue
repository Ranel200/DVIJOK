<template>
  <div class="crm-page">
    <AdminHeader
      :tabs="tabs"
      v-model:active-tab="activeTab"
      :action="action"
      @action-click="onAction"
    >
      <template #title-trailing>
        <div class="crm-filter">
          <span class="crm-filter__text">Все заказы</span>
          <ArrowIcon direction="down" :size="14" class="crm-filter__arrow" />
        </div>

        <div class="crm-filter">
          <span class="crm-filter__text">В работе</span>
          <CloseIcon :size="14" class="crm-filter__icon" />
        </div>

        <label class="crm-filter crm-filter--search">
          <img src="/admin/icons/search.svg" alt="" class="crm-filter__icon" />
          <input v-model="search" type="text" class="crm-filter__input" placeholder="Поиск" />
        </label>
      </template>

      <template v-if="activeTab === 'list'" #below>
        <div class="crm-list-bar">
          <span class="crm-list-bar__count">Все сделки ({{ filteredDealsCount }})</span>
          <BaseChoice
            v-model="statusFilter"
            shape="pill"
            :options="statusOptions"
            :multiple="true"
            :block="false"
            gap="10px"
            class="crm-list-bar__filters"
          />
        </div>
      </template>
    </AdminHeader>

    <CrmKanbanBoard
      v-show="activeTab === 'kanban'"
      :columns="columns"
      :search="search"
      :loading="loading"
    />

    <CrmDealsList
      v-show="activeTab === 'list'"
      :deals="deals"
      :search="search"
      :status-filter="statusFilter"
      :loading="listLoading"
      @delete="onDeleteDeal"
    />

    <OrderModal v-model="orderOpen" :order-number="0" :saving="orderSaving" @save="onSaveOrder" />

    <SuccessModal v-model="savedOpen" :message="savedMessage" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import CrmDealsList from '@/components/crm/CrmDealsList.vue'
import CrmKanbanBoard from '@/components/crm/CrmKanbanBoard.vue'
import OrderModal from '@/components/crm/OrderModal.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import CloseIcon from '@/components/ui/CloseIcon.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import { crmApi } from '@/api/index.js'
import { CRM_STATUS_LIST, filterCrmDeals, formatCrmOrderNumber } from '@/constants/crm.js'

const tabs = [
  { label: 'Канбан', value: 'kanban' },
  { label: 'Список', value: 'list' }
]
const activeTab = ref('kanban')

const action = { label: '+ Новый заказ' }

const search = ref('')

const columns = ref([])
const loading = ref(true)

const deals = ref([])
const listLoading = ref(true)
const statusFilter = ref([])

const orderOpen = ref(false)
const orderSaving = ref(false)
const savedOpen = ref(false)
const savedMessage = ref('')

const statusOptions = CRM_STATUS_LIST.map(({ value, label, color, bg }) => ({
  value,
  label,
  activeColor: color,
  activeBg: bg
}))

const filteredDealsCount = computed(
  () =>
    filterCrmDeals(deals.value, {
      search: search.value,
      statusFilter: statusFilter.value
    }).length
)

function onDeleteDeal(dealId) {
  deals.value = deals.value.filter(item => item.id !== dealId)
}

function onAction() {
  orderOpen.value = true
}

async function reloadCrm() {
  const [columnsResult, dealsResult] = await Promise.allSettled([
    crmApi.listColumns(),
    crmApi.listDeals()
  ])

  if (columnsResult.status === 'fulfilled') {
    columns.value = Array.isArray(columnsResult.value) ? columnsResult.value : []
  }

  if (dealsResult.status === 'fulfilled') {
    deals.value = (Array.isArray(dealsResult.value) ? dealsResult.value : []).map(deal => ({
      ...deal,
      _selected: false
    }))
  }
}

async function onSaveOrder(draft) {
  orderSaving.value = true
  try {
    const created = await crmApi.createOrder(draft)
    orderOpen.value = false
    await reloadCrm()
    savedMessage.value = `Заказ ${formatCrmOrderNumber(created.number)} создан!`
    savedOpen.value = true
  } finally {
    orderSaving.value = false
  }
}

onMounted(async () => {
  await reloadCrm()
  loading.value = false
  listLoading.value = false
})
</script>

<style scoped lang="scss">
.crm-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.crm-filter {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 11px 15px;
  width: 160px;
  box-sizing: border-box;
  border: 1px solid var(--dvijok-bg-dark);
  border-radius: 8px;
}

.crm-filter__text {
  color: var(--dvijok-bg-dark);
  font-size: 12px;
  line-height: 14px;
  font-weight: 400;
}

.crm-filter__arrow {
  color: var(--dvijok-bg-dark);
  flex-shrink: 0;
}

.crm-filter__icon {
  display: block;
  flex-shrink: 0;
}

.crm-filter--search {
  padding: 6px 10px;
  width: 220px;
}

.crm-filter__input {
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

.crm-list-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.crm-list-bar__count {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
  white-space: nowrap;
}

.crm-list-bar__filters {
  flex-wrap: nowrap;
}

.crm-list-bar__filters :deep(.base-choice__option) {
  border: none;
  background-color: color-mix(in srgb, var(--dvijok-link) 30%, transparent);
  color: var(--dvijok-text-primary);
}
</style>
