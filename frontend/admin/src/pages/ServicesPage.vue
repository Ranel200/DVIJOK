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
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import AdminTable from '@/components/ui/AdminTable.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import { servicesApi } from '@/api/index.js'
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
const choice = ref('all')
const services = ref([])
const menuServiceId = ref(null)
const menuStyle = ref({})
const menuAbove = ref(false)
const menuEl = ref(null)

const choices = [
  { label: 'Категория', value: 'category' },
  { label: 'Мастер', value: 'master' },
  { label: 'Цена', value: 'price' },
  { label: 'Все', value: 'all' }
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
  if (!query) return services.value
  return services.value.filter(service => service.title.toLowerCase().includes(query))
})

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

function onAction() {
  // TODO: открыть форму добавления услуги
}

function onDeleteSelected() {
  if (!hasSelected.value) return
  services.value = services.value.filter(service => !service._selected)
  closeMenu()
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

  // Меню выравнивается по правому краю кнопки (translateX(-100%))
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
  // Сначала меряем скрытым, чтобы не мигал неверный top
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
  closeMenu()
  // TODO: открыть форму редактирования услуги
}

function onDuplicateService() {
  const service = menuService.value
  if (!service) return
  const nextId = services.value.reduce((max, item) => Math.max(max, item.id), 0) + 1
  const copy = {
    ...service,
    id: nextId,
    title: `${service.title} (копия)`,
    master: { ...service.master },
    _selected: false
  }
  const index = services.value.findIndex(item => item.id === service.id)
  services.value.splice(index + 1, 0, copy)
  closeMenu()
}

function onToggleVisibility() {
  const service = menuService.value
  if (!service) return
  service.status = service.status === 'hidden' ? 'active' : 'hidden'
  closeMenu()
}

function onDeleteService() {
  const service = menuService.value
  if (!service) return
  services.value = services.value.filter(item => item.id !== service.id)
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

onMounted(async () => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('scroll', onDocumentScroll, true)
  document.addEventListener('keydown', onDocumentKeydown)
  try {
    const [summaryData, servicesData] = await Promise.all([
      servicesApi.summary(),
      servicesApi.list()
    ])
    summary.value = summaryData
    services.value = servicesData.map(service => ({ ...service, _selected: false }))
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
