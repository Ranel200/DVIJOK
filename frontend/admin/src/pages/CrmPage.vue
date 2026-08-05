<template>
  <div class="crm-page">
    <AdminHeader
      :tabs="tabs"
      v-model:active-tab="activeTab"
      :action="action"
      @action-click="onAction"
    >
      <template #title-trailing>
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
      @edit="onOpenOrder"
    />

    <CrmDealsList
      v-show="activeTab === 'list'"
      :deals="deals"
      :search="search"
      :status-filter="statusFilter"
      :loading="listLoading"
      @delete="onRequestDeleteDeal"
      @delete-selected="onRequestDeleteSelected"
      @open="onOpenOrder"
      @edit="onEditOrder"
    />

    <OrderModal
      v-model="orderOpen"
      :mode="orderMode"
      :order="activeOrder"
      :order-number="nextOrderNumber"
      :saving="orderSaving"
      @save="onSaveOrder"
      @edit="onStartEditOrder"
      @delete="onRequestDeleteFromModal"
    />

    <BaseModal v-model="deleteConfirmOpen">
      <div class="crm-confirm">
        <h2 class="crm-confirm__title">{{ deleteConfirmTitle }}</h2>
        <div class="crm-confirm__actions">
          <BaseButton color="green" size="lg" @click="closeDeleteConfirm">Отмена</BaseButton>
          <BaseButton color="red" size="lg" @click="confirmDelete">Удалить</BaseButton>
        </div>
      </div>
    </BaseModal>

    <SuccessModal v-model="savedOpen" :message="savedMessage" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import CrmDealsList from '@/components/crm/CrmDealsList.vue'
import CrmKanbanBoard from '@/components/crm/CrmKanbanBoard.vue'
import OrderModal from '@/components/crm/OrderModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
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
const orderMode = ref('create')
const activeOrder = ref(null)
const orderSaving = ref(false)
const savedOpen = ref(false)
const savedMessage = ref('')

const deleteConfirmOpen = ref(false)
const deleteMode = ref('single')
const pendingDeleteId = ref(null)
const pendingDeleteNumber = ref(0)

const statusOptions = CRM_STATUS_LIST.filter(({ value }) => value !== 'primary').map(
  ({ value, label, color, bg }) => ({
    value,
    label,
    activeColor: color,
    activeBg: bg
  })
)

const filteredDealsCount = computed(
  () =>
    filterCrmDeals(deals.value, {
      search: search.value,
      statusFilter: statusFilter.value
    }).length
)

const nextOrderNumber = computed(() => {
  const numbers = [
    ...deals.value.map(item => item.number),
    ...columns.value.flatMap(column => (column.items || []).map(item => item.number))
  ]
  return Math.max(0, ...numbers) + 1
})

const deleteConfirmTitle = computed(() => {
  if (deleteMode.value === 'selected') return 'Удалить выбранные заказы?'
  return `Удалить заказ ${formatCrmOrderNumber(pendingDeleteNumber.value)}?`
})

function removeDealsByIds(ids) {
  const idSet = new Set(ids)
  deals.value = deals.value.filter(item => !idSet.has(item.id))
  for (const column of columns.value) {
    column.items = column.items.filter(item => !idSet.has(item.id))
  }
}

function openDeleteConfirm({ mode = 'single', id = null, number = 0 } = {}) {
  deleteMode.value = mode
  pendingDeleteId.value = id
  pendingDeleteNumber.value = number
  deleteConfirmOpen.value = true
}

function closeDeleteConfirm() {
  deleteConfirmOpen.value = false
  deleteMode.value = 'single'
  pendingDeleteId.value = null
  pendingDeleteNumber.value = 0
}

function confirmDelete() {
  if (deleteMode.value === 'selected') {
    const ids = deals.value.filter(deal => deal._selected).map(deal => deal.id)
    removeDealsByIds(ids)
    closeDeleteConfirm()
    savedMessage.value = 'Выбранные заказы удалены!'
    savedOpen.value = true
    return
  }

  if (pendingDeleteId.value) {
    const number = pendingDeleteNumber.value
    removeDealsByIds([pendingDeleteId.value])
    closeDeleteConfirm()
    savedMessage.value = `Заказ ${formatCrmOrderNumber(number)} удален!`
    savedOpen.value = true
  }
}

function onRequestDeleteDeal(dealId) {
  const deal = deals.value.find(item => item.id === dealId)
  if (!deal) return
  openDeleteConfirm({ mode: 'single', id: deal.id, number: deal.number })
}

function onRequestDeleteSelected() {
  openDeleteConfirm({ mode: 'selected' })
}

function onAction() {
  activeOrder.value = null
  orderMode.value = 'create'
  orderOpen.value = true
}

function onOpenOrder(order) {
  activeOrder.value = order
  orderMode.value = 'view'
  orderOpen.value = true
}

function onEditOrder(order) {
  activeOrder.value = order
  orderMode.value = 'edit'
  orderOpen.value = true
}

function onStartEditOrder() {
  orderMode.value = 'edit'
}

function onRequestDeleteFromModal(order) {
  if (!order?.id) return
  orderOpen.value = false
  activeOrder.value = null
  orderMode.value = 'create'
  openDeleteConfirm({ mode: 'single', id: order.id, number: order.number })
}

function applyOrderDraft(target, draft) {
  const carBrand = [draft.brand, draft.model].filter(Boolean).join(' ').trim()
  target.status = draft.status
  target.clientName = draft.clientName
  target.phone = draft.phone
  target.email = draft.email
  target.description = draft.description
  target.date = draft.date
  target.time = draft.time
  target.source = draft.source
  target.plate = draft.plate
  target.carBrand = carBrand
  target.carYear = draft.year ? Number(draft.year) || null : null
  target.color = draft.color
  target.vin = draft.vin
  target.mileage = draft.mileage
  if (Array.isArray(draft.lines)) target.lines = draft.lines
  if (draft.amount != null) target.amount = draft.amount
  if (Array.isArray(draft.services)) target.services = draft.services
  if (draft.master !== undefined) target.master = draft.master
  if (draft.masters !== undefined) target.masters = draft.masters
}

function updateLocalOrder(draft) {
  const deal = deals.value.find(item => item.id === draft.id)
  if (deal) applyOrderDraft(deal, draft)

  let card = null
  let fromColumn = null
  for (const column of columns.value) {
    const index = column.items.findIndex(item => item.id === draft.id)
    if (index === -1) continue
    card = column.items[index]
    fromColumn = column
    column.items.splice(index, 1)
    break
  }

  if (!card) return
  applyOrderDraft(card, draft)

  const toColumn =
    columns.value.find(column => column.id === draft.status) || fromColumn || columns.value[0]
  toColumn?.items.unshift(card)
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
    if (draft.id) {
      updateLocalOrder(draft)
      orderOpen.value = false
      activeOrder.value = null
      orderMode.value = 'create'
      savedMessage.value = `Заказ ${formatCrmOrderNumber(draft.number)} сохранён!`
      savedOpen.value = true
      return
    }

    const created = await crmApi.createOrder(draft)
    orderOpen.value = false
    activeOrder.value = null
    orderMode.value = 'create'
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
  box-sizing: border-box;
  border: 1px solid var(--dvijok-bg-dark);
  border-radius: 8px;
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
  justify-content: space-between;
  gap: 10px;
}

.crm-list-bar__count {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  white-space: nowrap;
}

.crm-list-bar__filters {
  flex-wrap: nowrap;
  margin-left: auto;
}

.crm-list-bar__filters :deep(.base-choice__option) {
  border: none;
  background-color: color-mix(in srgb, var(--dvijok-link) 30%, transparent);
  color: var(--dvijok-text-primary);
}

.crm-confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.crm-confirm__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}

.crm-confirm__actions {
  display: flex;
  align-items: center;
  gap: 90px;
}
</style>
