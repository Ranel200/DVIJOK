<template>
  <div class="crm-list">
    <AdminTable
      :columns="listColumns"
      :loading="loading"
      :empty="!filteredDeals.length"
      empty-text="Нет сделок по выбранным фильтрам"
    >
      <template #head>
        <th class="admin-table__th admin-table__th--check crm-list__th--number" colspan="2">
          № сделки
        </th>
        <th class="admin-table__th crm-list__th--status">Статус</th>
        <th class="admin-table__th crm-list__th--client">Клиент</th>
        <th class="admin-table__th crm-list__th--amount">Сумма</th>
        <th class="admin-table__th crm-list__th--services">Услуги</th>
        <th class="admin-table__th crm-list__th--master">Мастер</th>
        <th class="admin-table__th crm-list__th--date">Дата</th>
        <th class="admin-table__th crm-list__th--actions"></th>
      </template>

      <tr v-for="deal in filteredDeals" :key="deal.id" class="admin-table__row">
        <td class="admin-table__cell admin-table__cell--check">
          <BaseCheckbox v-model="deal._selected" />
        </td>
        <td class="admin-table__cell crm-list__cell--number">
          <div class="crm-list__number">
            <span class="crm-list__number-id">{{ formatCrmOrderNumber(deal.number) }}</span>
            <span class="crm-list__number-date">{{ deal.createdAt }}</span>
          </div>
        </td>
        <td class="admin-table__cell crm-list__cell--status">
          <span class="crm-list__pill" :style="pillStyle(deal.status)">
            {{ crmStatusOption(deal.status).label }}
          </span>
        </td>
        <td class="admin-table__cell crm-list__cell--client">
          <div class="crm-list__client">
            <span class="crm-list__client-name">{{ deal.clientName }}</span>
            <span class="crm-list__client-car">{{ deal.carBrand }} · {{ deal.carYear }}</span>
          </div>
        </td>
        <td class="admin-table__cell crm-list__cell--amount">
          <span class="crm-list__amount">{{ formatCrmMoney(deal.amount) }} ₽</span>
        </td>
        <td class="admin-table__cell crm-list__cell--services">
          <div class="crm-list__services">
            <span v-for="service in deal.services" :key="service" class="crm-list__service">
              {{ service }}
            </span>
          </div>
        </td>
        <td class="admin-table__cell crm-list__cell--master">
          <span class="crm-list__master">{{ formatMaster(deal.master) }}</span>
        </td>
        <td class="admin-table__cell crm-list__cell--date">
          <div class="crm-list__date">
            <span class="crm-list__date-main">{{ deal.updatedAt }}</span>
            <span class="crm-list__date-sub">{{ deal.createdAt }}</span>
          </div>
        </td>
        <td class="admin-table__cell crm-list__cell--actions">
          <button
            type="button"
            class="crm-list__dots"
            aria-label="Действия"
            aria-haspopup="menu"
            :aria-expanded="menuDealId === deal.id"
            @click.stop="toggleMenu(deal, $event)"
          >
            <img src="/admin/icons/services/dots.svg" alt="" />
          </button>
        </td>
      </tr>
    </AdminTable>

    <Teleport to="body">
      <Transition name="crm-menu">
        <div
          v-if="menuDeal"
          ref="menuEl"
          class="crm-menu"
          :class="{ 'crm-menu--above': menuAbove }"
          role="menu"
          :style="menuStyle"
          @click.stop
        >
          <button type="button" class="crm-menu__item" role="menuitem" @click="onEditDeal">
            <div class="crm-menu__icon">
              <img src="/admin/icons/services/edit.svg" alt="" />
            </div>
            <span>Редактировать</span>
          </button>
          <button
            type="button"
            class="crm-menu__item crm-menu__item--danger"
            role="menuitem"
            @click="onDeleteDeal"
          >
            <div class="crm-menu__icon">
              <img src="/admin/icons/services/delete.svg" alt="" />
            </div>
            <span>Удалить</span>
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import AdminTable from '@/components/ui/AdminTable.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import {
  crmStatusOption,
  filterCrmDeals,
  formatCrmMoney,
  formatCrmOrderNumber
} from '@/constants/crm.js'

const props = defineProps({
  deals: {
    type: Array,
    default: () => []
  },
  search: {
    type: String,
    default: ''
  },
  statusFilter: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['delete'])

const menuDealId = ref(null)
const menuStyle = ref({})
const menuAbove = ref(false)
const menuEl = ref(null)

const listColumns = [
  { key: 'check', width: '63px' },
  { key: 'number', width: '90px' },
  { key: 'status', width: '105px' },
  { key: 'client', width: '160px' },
  { key: 'amount', width: '90px' },
  { key: 'services', width: '3fr' },
  { key: 'master', width: '110px' },
  { key: 'date', width: '75px' },
  { key: 'actions', width: '44px' }
]

const menuDeal = computed(() => props.deals.find(deal => deal.id === menuDealId.value))

const filteredDeals = computed(() =>
  filterCrmDeals(props.deals, {
    search: props.search,
    statusFilter: props.statusFilter
  })
)

function pillStyle(status) {
  const { color, bg } = crmStatusOption(status)
  return { color, backgroundColor: bg }
}

function formatMaster(master) {
  const parts = (master || '').split(' ').filter(Boolean)
  const lastName = parts[0] || ''
  const firstInitial = parts[1] ? `${parts[1][0]}.` : ''
  return `${lastName}${firstInitial ? ' ' + firstInitial : ''}`.trim()
}

function closeMenu() {
  menuDealId.value = null
}

function positionMenu(anchorRect) {
  const el = menuEl.value
  if (!el) return

  const menuRect = el.getBoundingClientRect()
  const gap = 4
  const pad = 8
  const maxTop = window.innerHeight - pad - menuRect.height
  let top = anchorRect.bottom + gap
  let above = false

  if (top > maxTop) {
    top = anchorRect.top - gap - menuRect.height
    above = true
  }

  top = Math.min(Math.max(top, pad), Math.max(pad, maxTop))

  let left = anchorRect.right
  left = Math.min(Math.max(left, pad + menuRect.width), window.innerWidth - pad)

  menuAbove.value = above
  menuStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

async function toggleMenu(deal, event) {
  if (menuDealId.value === deal.id) {
    closeMenu()
    return
  }
  const rect = event.currentTarget.getBoundingClientRect()
  menuAbove.value = false
  menuStyle.value = {
    top: `${rect.bottom + 4}px`,
    left: `${rect.right}px`,
    visibility: 'hidden'
  }
  menuDealId.value = deal.id
  await nextTick()
  positionMenu(rect)
}

function onEditDeal() {
  closeMenu()
}

function onDeleteDeal() {
  const deal = menuDeal.value
  if (!deal) return
  emit('delete', deal.id)
  closeMenu()
}

function onDocumentClick() {
  closeMenu()
}

function onDocumentScroll() {
  closeMenu()
}

function onDocumentKeydown(event) {
  if (event.key === 'Escape') closeMenu()
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('scroll', onDocumentScroll, true)
  document.addEventListener('keydown', onDocumentKeydown)
})

onBeforeUnmount(() => {
  closeMenu()
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('scroll', onDocumentScroll, true)
  document.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<style scoped lang="scss">
.crm-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.crm-list__th--number,
.crm-list__cell--number,
.crm-list__th--status,
.crm-list__cell--status,
.crm-list__th--client,
.crm-list__cell--client,
.crm-list__th--amount,
.crm-list__cell--amount,
.crm-list__th--services,
.crm-list__cell--services,
.crm-list__th--master,
.crm-list__cell--master,
.crm-list__th--date,
.crm-list__cell--date {
  padding-right: 20px;
}

.crm-list__th--actions,
.crm-list__cell--actions {
  padding-right: 19px;
  text-align: right;
}

.crm-list__number {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.crm-list__number-id {
  font-weight: 700;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm-list__number-date {
  font-weight: 400;
  font-size: 8px;
  line-height: 10px;
  color: var(--dvijok-text-secondary);
}

.crm-list__pill {
  display: inline-block;
  padding: 6px 10px;
  border: none;
  border-radius: 50px;
  font-weight: 500;
  font-size: 8px;
  line-height: 10px;
  white-space: nowrap;
}

.crm-list__client {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 160px;
  min-width: 0;
}

.crm-list__client-name,
.crm-list__client-car {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.crm-list__client-name {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm-list__client-car {
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
}

.crm-list__amount {
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link-hover);
  white-space: nowrap;
}

.crm-list__services {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.crm-list__service {
  padding: 6px 10px;
  border-radius: 50px;
  background: var(--dvijok-muted);
  font-weight: 400;
  font-size: 8px;
  line-height: 10px;
  color: var(--dvijok-blue-primary);
  white-space: normal;
  overflow-wrap: anywhere;
}

.crm-list__master {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
  white-space: nowrap;
}

.crm-list__date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.crm-list__date-main {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm-list__date-sub {
  font-weight: 400;
  font-size: 8px;
  line-height: 10px;
  color: var(--dvijok-link-hover);
}

.crm-list__dots {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.crm-list__dots img {
  display: block;
}

.crm-menu {
  position: fixed;
  z-index: 3000;
  transform: translateX(-100%);
  transform-origin: top right;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px;
  box-sizing: border-box;
  background-color: var(--dvijok-white);
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
}

.crm-menu--above {
  transform-origin: bottom right;
}

.crm-menu-enter-active,
.crm-menu-leave-active {
  transition:
    opacity 0.16s ease,
    transform 0.16s ease;
}

.crm-menu-enter-from,
.crm-menu-leave-to {
  opacity: 0;
  transform: translateX(-100%) scale(0.96) translateY(-4px);
}

.crm-menu--above.crm-menu-enter-from,
.crm-menu--above.crm-menu-leave-to {
  transform: translateX(-100%) scale(0.96) translateY(4px);
}

.crm-menu-enter-to,
.crm-menu-leave-from {
  opacity: 1;
  transform: translateX(-100%) scale(1) translateY(0);
}

.crm-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  text-align: left;
  white-space: nowrap;
  font-weight: 400;
  font-size: 12px;
  line-height: 100%;
  color: var(--dvijok-blue-primary);
}

.crm-menu__item--danger {
  color: var(--dvijok-danger-strong);
}

.crm-menu__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.crm-menu__icon img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}
</style>
