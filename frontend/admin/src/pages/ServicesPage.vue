<template>
  <div class="services-page">
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
          <div class="services-filters__right">
            <BaseSelect
              v-model="employee"
              :options="employeeOptions"
              placeholder="Все сотрудники"
              class="services-filters__select"
            />
            <button
              type="button"
              class="services-filter-btn"
              :aria-label="
                priceSort === 'asc'
                  ? 'Сортировка по цене: возрастание'
                  : 'Сортировка по цене: снижение'
              "
              @click="togglePriceSort"
            >
              <span>Цена</span>
              <img
                src="/admin/icons/services/direction.svg"
                alt=""
                class="services-filter-btn__direction"
                :class="{ 'services-filter-btn__direction--desc': priceSort === 'desc' }"
              />
            </button>
            <BaseSelect
              v-model="statusFilter"
              variant="accent"
              :options="statusFilterOptions"
              class="services-filters__status"
            />
          </div>
        </div>
      </template>
    </AdminHeader>
    <AdminTable
      :columns="columns"
      :loading="loading"
      :empty="!filteredServices.length"
      empty-text="Нет услуг по выбранным фильтрам"
    >
      <template #head>
        <th class="admin-table__th admin-table__th--check"></th>
        <th class="admin-table__th services__th--name">Название услуги</th>
        <th class="admin-table__th services__th--master">Мастер</th>
        <th class="admin-table__th services__th--price">Цена услуги ₽</th>
        <th class="admin-table__th services__th--duration">Длит.</th>
        <th class="admin-table__th services__th--orders">Заказов</th>
        <th class="admin-table__th services__th--status">Статус</th>
        <th class="admin-table__th services__th--actions"></th>
      </template>

      <tr v-for="service in filteredServices" :key="service.id" class="admin-table__row">
        <td class="admin-table__cell admin-table__cell--check">
          <BaseCheckbox v-model="service._selected" />
        </td>
        <td class="admin-table__cell services__cell--name">
          <div class="admin-table__title">{{ service.title }}</div>
          <div class="admin-table__desc">{{ service.description }}</div>
        </td>
        <td class="admin-table__cell services__cell--master">
          <span class="admin-table__text">{{ formatMaster(service.master) }}</span>
        </td>
        <td class="admin-table__cell services__cell--price">
          <div class="admin-table__title">{{ formatRubles(service.price) }}</div>
          <div class="admin-table__desc">{{ service.priceNote }}</div>
        </td>
        <td class="admin-table__cell services__cell--duration">
          <span class="admin-table__text">{{ service.durationHours }} ч</span>
        </td>
        <td class="admin-table__cell services__cell--orders">
          <div class="services__orders">
            <div class="services__orders-bar">
              <div
                class="services__orders-bar-fill"
                :style="{ width: ordersBarWidth(service.ordersCount) }"
              />
            </div>
            <div class="services__orders-count">
              {{ service.ordersCount }}
              {{ pluralize(service.ordersCount, ['заказ', 'заказа', 'заказов']) }}
            </div>
          </div>
        </td>
        <td class="admin-table__cell services__cell--status">
          <span :class="`services__pill services__pill--${service.status}`">
            {{ statusLabel(service.status) }}
          </span>
        </td>
        <td class="admin-table__cell services__cell--actions">
          <button
            type="button"
            class="services__dots"
            aria-label="Действия"
            aria-haspopup="menu"
            :aria-expanded="menuServiceId === service.id"
            @click.stop="toggleMenu(service, $event)"
          >
            <img src="/admin/icons/services/dots.svg" alt="" />
          </button>
        </td>
      </tr>

      <template #footer>
        <BaseButton color="red" size="lg" :disable="!hasSelected" @click="onDeleteSelected">
          Удалить выбранные
        </BaseButton>
      </template>
    </AdminTable>

    <Teleport to="body">
      <Transition name="services-menu">
        <div
          v-if="menuService"
          ref="menuEl"
          class="services-menu"
          :class="{ 'services-menu--above': menuAbove }"
          role="menu"
          :style="menuStyle"
          @click.stop
        >
          <button type="button" class="services-menu__item" role="menuitem" @click="onEditService">
            <div class="services-menu__icon">
              <img src="/admin/icons/services/edit.svg" alt="" />
            </div>
            <span>Редактировать</span>
          </button>
          <button
            type="button"
            class="services-menu__item"
            role="menuitem"
            @click="onDuplicateService"
          >
            <div class="services-menu__icon">
              <img src="/admin/icons/services/copy.svg" alt="" />
            </div>
            <span>Дублировать</span>
          </button>
          <button
            type="button"
            class="services-menu__item"
            role="menuitem"
            @click="onToggleVisibility"
          >
            <div class="services-menu__icon">
              <EyeIcon
                :closed="menuService.status !== 'hidden'"
                :size="16"
                color="var(--dvijok-blue-primary)"
              />
            </div>
            <span>{{ menuService.status === 'hidden' ? 'Показать' : 'Скрыть' }}</span>
          </button>
          <button
            type="button"
            class="services-menu__item services-menu__item--danger"
            role="menuitem"
            @click="onDeleteService"
          >
            <div class="services-menu__icon">
              <img src="/admin/icons/services/delete.svg" alt="" />
            </div>
            <span>Удалить</span>
          </button>
        </div>
      </Transition>
    </Teleport>

    <ServiceFormModal
      v-model="formOpen"
      :service="editingService"
      :employees="employees"
      :saving="formSaving"
      @save="onSaveService"
    />

    <BaseModal v-model="deleteConfirmOpen">
      <div class="services-confirm">
        <h2 class="services-confirm__title">{{ deleteConfirmTitle }}</h2>
        <div class="services-confirm__actions">
          <BaseButton color="green" size="lg" @click="closeDeleteConfirm">Отмена</BaseButton>
          <BaseButton color="red" size="lg" @click="confirmDelete">Удалить</BaseButton>
        </div>
      </div>
    </BaseModal>

    <SuccessModal v-model="resultOpen" :message="resultMessage" />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import ServiceFormModal from '@/components/services/ServiceFormModal.vue'
import AdminTable from '@/components/ui/AdminTable.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import { servicesApi, tasksApi } from '@/api/index.js'
import { pluralize } from '@/utils/pluralize.js'

const action = { label: '+ Добавить услугу' }

const columns = [
  { key: 'check', width: '63px' },
  { key: 'name', width: '3fr' },
  { key: 'master', width: '2fr' },
  { key: 'price', width: '150px' },
  { key: 'duration', width: '70px' },
  { key: 'orders', width: '110px' },
  { key: 'status', width: '90px' },
  { key: 'actions', width: '44px' }
]

const summary = ref(null)
const loading = ref(true)
const search = ref('')
const employee = ref('all')
const priceSort = ref('asc')
const statusFilter = ref('all')
const services = ref([])
const employees = ref([])
const menuServiceId = ref(null)
const menuStyle = ref({})
const menuAbove = ref(false)
const menuEl = ref(null)

const formOpen = ref(false)
const formSaving = ref(false)
const editingService = ref(null)

const deleteConfirmOpen = ref(false)
const deleteMode = ref('single')
const pendingDeleteId = ref(null)
const pendingDeleteTitle = ref('')

const resultOpen = ref(false)
const resultMessage = ref('')

const deleteConfirmTitle = computed(() => {
  if (deleteMode.value === 'selected') {
    return 'Удалить выбранные услуги?'
  }
  return `Удалить услугу "${pendingDeleteTitle.value}"?`
})

const employeeOptions = computed(() => [
  { value: 'all', label: 'Все сотрудники' },
  ...employees.value.map(e => ({ value: e.id, label: e.name }))
])

const statusFilterOptions = [
  { label: 'Все услуги', value: 'all' },
  { label: 'Активны', value: 'active' },
  { label: 'Скрыты', value: 'hidden' }
]

const statusLabels = {
  active: 'Активна',
  hidden: 'Скрыта'
}

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

const maxOrders = computed(() =>
  services.value.reduce((max, service) => Math.max(max, service.ordersCount || 0), 0)
)

const filteredServices = computed(() => {
  const query = search.value.trim().toLowerCase()
  const list = services.value.filter(service => {
    const titleOk = !query || service.title.toLowerCase().includes(query)
    const employeeOk =
      employee.value === 'all' ||
      service.master?.id === employee.value ||
      service.masters?.some(item => item.id === employee.value)
    const statusOk = statusFilter.value === 'all' || service.status === statusFilter.value
    return titleOk && employeeOk && statusOk
  })

  const direction = priceSort.value === 'asc' ? 1 : -1
  return [...list].sort((a, b) => ((a.price || 0) - (b.price || 0)) * direction)
})

function togglePriceSort() {
  priceSort.value = priceSort.value === 'asc' ? 'desc' : 'asc'
}

const menuService = computed(() =>
  services.value.find(service => service.id === menuServiceId.value)
)

const hasSelected = computed(() => filteredServices.value.some(service => service._selected))

watch(filteredServices, visible => {
  const visibleIds = new Set(visible.map(service => service.id))
  for (const service of services.value) {
    if (service._selected && !visibleIds.has(service.id)) {
      service._selected = false
    }
  }
})

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

function statusLabel(value) {
  return statusLabels[value] || value
}

function formatRubles(value) {
  return `${formatNumber(value)} ₽`
}

function formatNumber(value) {
  return new Intl.NumberFormat('ru-RU').format(value)
}

function formatMaster(master) {
  const parts = (master?.name || '').split(' ').filter(Boolean)
  const lastName = parts[0] || ''
  const firstInitial = parts[1] ? `${parts[1][0]}.` : ''
  return `${lastName}${firstInitial ? ' ' + firstInitial : ''}`.trim()
}

function ordersBarWidth(count) {
  if (!maxOrders.value) return '50%'
  return `${Math.round((count / maxOrders.value) * 100)}%`
}

function toServicePayload(service, overrides = {}) {
  const masters = Array.isArray(service.masters)
    ? service.masters.map(item => item?.id ?? item).filter(Boolean)
    : []
  return {
    title: service.title,
    description: service.description || '',
    category: service.category || '',
    priceType: service.priceType || 'fixed',
    price: Number(service.price) || 0,
    priceTo: service.priceTo ?? null,
    duration: Number(service.durationHours) || 0,
    durationUnit: 'hours',
    status: service.status === 'hidden' ? 'hidden' : 'active',
    masters: masters.length ? masters : ['all'],
    notes: service.notes || '',
    ...overrides
  }
}

function onAction() {
  editingService.value = null
  formOpen.value = true
}

function onDeleteSelected() {
  if (!hasSelected.value) return
  deleteMode.value = 'selected'
  pendingDeleteId.value = null
  pendingDeleteTitle.value = ''
  deleteConfirmOpen.value = true
  closeMenu()
}

function closeDeleteConfirm() {
  deleteConfirmOpen.value = false
  deleteMode.value = 'single'
  pendingDeleteId.value = null
  pendingDeleteTitle.value = ''
}

function closeMenu() {
  menuServiceId.value = null
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

async function toggleMenu(service, event) {
  if (menuServiceId.value === service.id) {
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
  menuServiceId.value = service.id
  await nextTick()
  positionMenu(rect)
}

function onEditService() {
  const service = menuService.value
  if (!service) return
  editingService.value = { ...service }
  formOpen.value = true
  closeMenu()
}

async function onDuplicateService() {
  const service = menuService.value
  if (!service) return
  const copy = await servicesApi.create(
    toServicePayload(service, { title: `${service.title} (копия)` })
  )
  const index = services.value.findIndex(item => item.id === service.id)
  services.value.splice(index + 1, 0, { ...copy, _selected: false })
  closeMenu()
}

async function onToggleVisibility() {
  const service = menuService.value
  if (!service) return
  const status = service.status === 'hidden' ? 'active' : 'hidden'
  const updated = await servicesApi.update(service.id, toServicePayload(service, { status }))
  Object.assign(service, updated, { _selected: service._selected })
  closeMenu()
}

function onDeleteService() {
  const service = menuService.value
  if (!service) return
  deleteMode.value = 'single'
  pendingDeleteId.value = service.id
  pendingDeleteTitle.value = service.title
  deleteConfirmOpen.value = true
  closeMenu()
}

async function confirmDelete() {
  if (deleteMode.value === 'selected') {
    const ids = services.value.filter(service => service._selected).map(service => service.id)
    await servicesApi.removeMany(ids)
    services.value = services.value.filter(service => !service._selected)
    closeDeleteConfirm()
    resultMessage.value = 'Выбранные услуги удалены!'
    resultOpen.value = true
    return
  }

  const id = pendingDeleteId.value
  const title = pendingDeleteTitle.value
  if (id == null) return
  await servicesApi.remove(id)
  services.value = services.value.filter(item => item.id !== id)
  closeDeleteConfirm()
  resultMessage.value = `Услуга "${title}" удалена!`
  resultOpen.value = true
}

async function onSaveService(draft) {
  formSaving.value = true
  try {
    if (editingService.value?.id) {
      const updated = await servicesApi.update(editingService.value.id, {
        ...draft,
        priceTo: editingService.value.priceTo ?? null
      })
      const index = services.value.findIndex(item => item.id === updated.id)
      if (index !== -1) services.value.splice(index, 1, { ...updated, _selected: false })
      resultMessage.value = `Услуга "${draft.title}" обновлена!`
    } else {
      const created = await servicesApi.create({ ...draft, priceTo: null })
      services.value.unshift({ ...created, _selected: false })
      resultMessage.value = `Услуга "${draft.title}" добавлена!`
    }

    formOpen.value = false
    editingService.value = null
    resultOpen.value = true
  } finally {
    formSaving.value = false
  }
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

onMounted(async () => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('scroll', onDocumentScroll, true)
  document.addEventListener('keydown', onDocumentKeydown)
  try {
    const [summaryData, servicesData, employeesData] = await Promise.all([
      servicesApi.summary(),
      servicesApi.list(),
      tasksApi.employees()
    ])
    summary.value = summaryData
    services.value = servicesData.map(service => ({ ...service, _selected: false }))
    employees.value = employeesData
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('scroll', onDocumentScroll, true)
  document.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<style scoped lang="scss">
.services-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.services__th--name,
.services__cell--name,
.services__th--master,
.services__cell--master {
  padding-right: 40px;
}

.services__th--price,
.services__cell--price,
.services__th--duration,
.services__cell--duration,
.services__th--orders,
.services__cell--orders,
.services__th--status,
.services__cell--status {
  padding-right: 40px;
}

.services__th--actions,
.services__cell--actions {
  padding-right: 19px;
  text-align: right;
}

.services__orders {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.services__orders-bar {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background-color: var(--dvijok-progress-track);
  overflow: hidden;
}

.services__orders-bar-fill {
  height: 100%;
  border-radius: 3px;
  background-color: var(--dvijok-blue-primary);
}

.services__orders-count {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.services__pill {
  display: inline-block;
  padding: 6px 10px;
  min-width: 55px;
  box-sizing: border-box;
  border: none;
  border-radius: 50px;
  text-align: center;
  font-weight: 500;
  font-size: 8px;
  line-height: 10px;
}

.services__pill--active {
  background-color: var(--dvijok-success-bg);
  color: var(--dvijok-success);
}

.services__pill--hidden {
  background-color: var(--dvijok-muted);
  color: var(--dvijok-text-secondary);
}

.services__dots {
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

.services__dots img {
  display: block;
}

.services-menu {
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

.services-menu--above {
  transform-origin: bottom right;
}

.services-menu-enter-active,
.services-menu-leave-active {
  transition:
    opacity 0.16s ease,
    transform 0.16s ease;
}

.services-menu-enter-from,
.services-menu-leave-to {
  opacity: 0;
  transform: translateX(-100%) scale(0.96) translateY(-4px);
}

.services-menu--above.services-menu-enter-from,
.services-menu--above.services-menu-leave-to {
  transform: translateX(-100%) scale(0.96) translateY(4px);
}

.services-menu-enter-to,
.services-menu-leave-from {
  opacity: 1;
  transform: translateX(-100%) scale(1) translateY(0);
}

.services-menu__item {
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

.services-menu__item--danger {
  color: var(--dvijok-danger-strong);
}

.services-menu__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.services-menu__icon img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.services-filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  margin-top: 16px;
}

.services-filters__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.services-filters__select {
  width: 180px;
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

.services-filter-btn {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 110px;
  padding: 9px;
  box-sizing: border-box;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 8px;
  background-color: var(--dvijok-white);
  cursor: pointer;
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;
  color: var(--dvijok-text-secondary);
  text-align: left;
}

.services-filter-btn__direction {
  display: block;
  width: 16px;
  height: auto;
  flex-shrink: 0;
  transition: transform 0.18s ease;
}

.services-filter-btn__direction--desc {
  transform: scaleY(-1);
}

.services-filters__status {
  width: 130px;
}

.services-confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.services-confirm__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}

.services-confirm__actions {
  display: flex;
  align-items: center;
  gap: 90px;
}
</style>
