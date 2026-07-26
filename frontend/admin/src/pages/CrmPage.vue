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
          <img src="/admin/icons/close-14.svg" alt="" class="crm-filter__icon" />
        </div>

        <label class="crm-filter crm-filter--search">
          <img src="/admin/icons/search.svg" alt="" class="crm-filter__icon" />
          <input v-model="search" type="text" class="crm-filter__input" placeholder="Поиск" />
        </label>
      </template>
    </AdminHeader>

    <div v-show="activeTab === 'kanban'" class="crm">
      <div v-if="loading" class="crm__loading" aria-live="polite">Загрузка доски…</div>
      <template v-else>
      <div
        v-show="boardScrollable"
        ref="scrollbarRef"
        class="crm__scrollbar"
        @pointerdown="onTrackPointerDown"
      >
        <div
          ref="thumbRef"
          class="crm__scrollbar-thumb"
          :class="{ 'crm__scrollbar-thumb--dragging': thumbDragging }"
          :style="thumbStyle"
          @pointerdown="onThumbPointerDown"
        />
      </div>

      <div
        ref="boardWrapRef"
        class="crm__board-wrap"
        @pointerenter="onBoardEnter"
        @pointerleave="onBoardLeave"
        @pointermove="onBoardMove"
      >
        <button
          v-show="boardScrollable && canScrollLeft"
          type="button"
          class="crm__nav crm__nav--left"
          :class="{ 'crm__nav--visible': navLeftVisible }"
          aria-label="Прокрутить влево"
          @click="scrollByColumn(-1)"
        >
          <ArrowIcon direction="left" :size="16" color="#0B3CBA69" class="crm__nav-arrow" />
        </button>

        <div ref="boardRef" class="crm__board" @scroll="updateThumb">
          <div v-for="column in columns" :key="column.id" class="crm__column">
            <header class="crm__column-header" :style="{ background: column.gradient }">
              <div class="crm__column-title-row">
                <h2 class="crm__column-title">{{ column.title }}</h2>
                <span class="crm__column-pill">
                  <span class="crm__column-pill-count">{{
                    columnStats[column.id]?.count ?? 0
                  }}</span>
                </span>
              </div>
              <p class="crm__column-sum">
                Общая сумма {{ columnStats[column.id]?.sumFormatted ?? '0' }} ₽
              </p>
            </header>

            <div class="crm__column-body">
              <VueDraggable
                v-model="getColumnItemsModel(column).value"
                group="crm"
                class="crm__list"
                :animation="200"
                ghost-class="crm__card--ghost"
                drag-class="crm__card--drag"
                :scroll="true"
                :bubble-scroll="true"
                :scroll-sensitivity="48"
                :scroll-speed="14"
                @start="onDragStart"
                @end="onDragEnd"
              >
                <article
                  v-for="element in getColumnItemsModel(column).value"
                  :key="element.id"
                  class="crm__card"
                >
                  <div class="crm__card-top">
                    <h3 class="crm__card-number">{{ formatOrderNumber(element.number) }}</h3>
                    <button
                      type="button"
                      class="crm__card-edit"
                      aria-label="Редактировать"
                      @pointerdown.stop
                    >
                      <img src="/admin/icons/services/edit.svg" alt="" />
                    </button>
                  </div>

                  <div class="crm__card-divider" aria-hidden="true" />

                  <div class="crm__card-body">
                    <p class="crm__card-price">{{ formatMoney(element.amount) }} ₽</p>

                    <div class="crm__card-meta">
                      <span>{{ element.clientName }}</span>
                      <span>{{ element.phone }}</span>
                    </div>

                    <div class="crm__card-meta">
                      <span>{{ element.carBrand }}</span>
                      <span>{{ element.plate }}</span>
                    </div>

                    <div class="crm__card-actions">
                      <button
                        type="button"
                        class="crm__card-action"
                        aria-label="Позвонить"
                        @pointerdown.stop
                      >
                        <img src="/admin/icons/crm/phone.svg" alt="" />
                      </button>
                      <button
                        type="button"
                        class="crm__card-action"
                        aria-label="Написать на почту"
                        @pointerdown.stop
                      >
                        <img src="/admin/icons/crm/mail.svg" alt="" />
                      </button>
                      <button
                        type="button"
                        class="crm__card-action"
                        aria-label="Отправить SMS"
                        @pointerdown.stop
                      >
                        <img src="/admin/icons/crm/sms.svg" alt="" />
                      </button>
                    </div>

                    <div class="crm__card-services">
                      <div class="crm__card-pills">
                        <span
                          v-for="service in element.services"
                          :key="service"
                          class="crm__card-pill"
                        >
                          {{ service }}
                        </span>
                      </div>
                      <p class="crm__card-masters">
                        <span class="crm__card-masters-label">Мастера:</span>
                        {{ element.masters }}
                      </p>
                    </div>
                  </div>

                  <div class="crm__card-dates">
                    <p>
                      <span class="crm__card-dates-label">Создано:</span>
                      {{ element.createdAt }}
                    </p>
                    <p>
                      <span class="crm__card-dates-label">Последние изменения:</span>
                      {{ element.updatedAt }}
                    </p>
                  </div>
                </article>
              </VueDraggable>
            </div>
          </div>
        </div>

        <button
          v-show="boardScrollable && canScrollRight"
          type="button"
          class="crm__nav crm__nav--right"
          :class="{ 'crm__nav--visible': navRightVisible }"
          aria-label="Прокрутить вправо"
          @click="scrollByColumn(1)"
        >
          <ArrowIcon direction="right" :size="16" color="#0B3CBA69" class="crm__nav-arrow" />
        </button>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import { crmApi } from '@/api/index.js'

const tabs = [
  { label: 'Канбан', value: 'kanban' },
  { label: 'Список', value: 'list' }
]
const activeTab = ref('kanban')

const action = { label: '+ Новый заказ' }

const search = ref('')

const columns = ref([])
const loading = ref(true)

const columnItemsModels = new Map()

function getColumnItemsModel(column) {
  let model = columnItemsModels.get(column.id)
  if (!model) {
    model = computed({
      get: () => column.items.filter(matchesSearch),
      set: (nextFiltered) => {
        column.items = mergeFilteredIntoSource(column.items, nextFiltered)
      }
    })
    columnItemsModels.set(column.id, model)
  }
  return model
}

function mergeFilteredIntoSource(source, nextFiltered) {
  const result = []
  let fi = 0
  for (const item of source) {
    if (matchesSearch(item)) {
      if (fi < nextFiltered.length) {
        result.push(nextFiltered[fi])
        fi++
      }
    } else {
      result.push(item)
    }
  }
  while (fi < nextFiltered.length) {
    result.push(nextFiltered[fi])
    fi++
  }
  return result
}

const boardRef = ref(null)
const boardWrapRef = ref(null)
const scrollbarRef = ref(null)
const thumbRef = ref(null)
const boardScrollable = ref(false)
const thumbLeft = ref(0)
const thumbDragging = ref(false)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const navLeftVisible = ref(false)
const navRightVisible = ref(false)

const NAV_EDGE_PX = 90

const EDGE_PX = 64
const MAX_SPEED = 8

let dragging = false
let pointerX = 0
let pointerY = 0
let autoScrollRaf = 0
let thumbDragOffset = 0
let cachedColumnBodies = null

const thumbStyle = computed(() => ({
  transform: `translateX(${thumbLeft.value}px)`
}))

function formatMoney(value) {
  return Number(value || 0).toLocaleString('ru-RU')
}

function formatOrderNumber(number) {
  return `№${String(number).padStart(3, '0')}`
}

function matchesSearch(element) {
  const query = search.value.trim().toLowerCase()
  if (!query) return true
  const numberStr = String(element.number)
  const formatted = formatOrderNumber(element.number).toLowerCase()
  const name = (element.clientName || '').toLowerCase()
  return numberStr.includes(query) || formatted.includes(query) || name.includes(query)
}

const columnStats = computed(() => {
  const stats = {}
  for (const column of columns.value) {
    const visible = column.items.filter(matchesSearch)
    const sum = visible.reduce((total, item) => total + (Number(item.amount) || 0), 0)
    stats[column.id] = {
      count: visible.length,
      sumFormatted: formatMoney(sum)
    }
  }
  return stats
})

function clamp01(value) {
  return Math.min(1, Math.max(0, value))
}

function edgeSpeed(distance) {
  return MAX_SPEED * clamp01(1 - distance / EDGE_PX)
}

function findColumnBodyAt(x) {
  const board = boardRef.value
  if (!board) return null
  if (!cachedColumnBodies) {
    cachedColumnBodies = Array.from(board.querySelectorAll('.crm__column-body'))
  }
  for (const body of cachedColumnBodies) {
    const rect = body.getBoundingClientRect()
    if (x >= rect.left && x <= rect.right) return body
  }
  return null
}

function trackPointer(event) {
  if (event.clientX == null || event.clientY == null) return
  pointerX = event.clientX
  pointerY = event.clientY
}

function tickAutoScroll() {
  if (!dragging) return

  const board = boardRef.value
  if (board) {
    const rect = board.getBoundingClientRect()
    let scrolledX = 0
    if (pointerX < rect.left + EDGE_PX) {
      scrolledX = -edgeSpeed(pointerX - rect.left)
    } else if (pointerX > rect.right - EDGE_PX) {
      scrolledX = edgeSpeed(rect.right - pointerX)
    }
    if (scrolledX !== 0) {
      board.scrollLeft += scrolledX
      updateThumb()
    }
  }

  const body = findColumnBodyAt(pointerX)
  if (body) {
    const rect = body.getBoundingClientRect()
    let scrolledY = 0
    if (pointerY < rect.top + EDGE_PX) {
      scrolledY = -edgeSpeed(pointerY - rect.top)
    } else if (pointerY > rect.bottom - EDGE_PX) {
      scrolledY = edgeSpeed(rect.bottom - pointerY)
    }
    if (scrolledY !== 0) body.scrollTop += scrolledY
  }

  autoScrollRaf = requestAnimationFrame(tickAutoScroll)
}

function onDragStart() {
  dragging = true
  window.addEventListener('pointermove', trackPointer, true)
  autoScrollRaf = requestAnimationFrame(tickAutoScroll)
}

function onDragEnd() {
  dragging = false
  cachedColumnBodies = null
  window.removeEventListener('pointermove', trackPointer, true)
  if (autoScrollRaf) {
    cancelAnimationFrame(autoScrollRaf)
    autoScrollRaf = 0
  }
  nextTick(updateThumb)
}

async function updateThumb() {
  const el = boardRef.value
  if (!el) {
    boardScrollable.value = false
    return
  }
  const trackWidth = el.clientWidth
  const maxScroll = el.scrollWidth - trackWidth
  const wasScrollable = boardScrollable.value
  boardScrollable.value = maxScroll > 1
  if (!boardScrollable.value) return
  if (!wasScrollable) await nextTick()
  if (!thumbRef.value) return
  const thumbWidth = thumbRef.value.offsetWidth
  const ratio = maxScroll > 0 ? el.scrollLeft / maxScroll : 0
  thumbLeft.value = ratio * (trackWidth - thumbWidth)
  canScrollLeft.value = el.scrollLeft > 1
  canScrollRight.value = el.scrollLeft < maxScroll - 1
}

function scrollByColumn(direction) {
  const board = boardRef.value
  if (!board) return
  const column = board.querySelector('.crm__column')
  if (!column) return
  const style = window.getComputedStyle(board)
  const gap = parseFloat(style.columnGap || style.gap || '20') || 20
  const step = column.offsetWidth + gap
  board.scrollBy({ left: step * direction, behavior: 'smooth' })
}

function onBoardEnter(event) {
  updateNavVisibility(event)
}

function onBoardLeave() {
  navLeftVisible.value = false
  navRightVisible.value = false
}

function onBoardMove(event) {
  updateNavVisibility(event)
}

function updateNavVisibility(event) {
  const wrap = boardWrapRef.value
  if (!wrap) return
  const rect = wrap.getBoundingClientRect()
  const x = event.clientX
  navLeftVisible.value = canScrollLeft.value && x - rect.left < NAV_EDGE_PX
  navRightVisible.value = canScrollRight.value && rect.right - x < NAV_EDGE_PX
}

function setBoardScrollByThumbLeft(nextLeft) {
  const board = boardRef.value
  const thumb = thumbRef.value
  if (!board || !thumb) return
  const trackWidth = board.clientWidth
  const thumbWidth = thumb.offsetWidth
  const maxThumbLeft = Math.max(0, trackWidth - thumbWidth)
  const clampedLeft = Math.min(maxThumbLeft, Math.max(0, nextLeft))
  const maxScroll = board.scrollWidth - trackWidth
  board.scrollLeft = maxThumbLeft > 0 ? (clampedLeft / maxThumbLeft) * maxScroll : 0
}

function onThumbPointerMove(event) {
  if (!thumbDragging.value) return
  const track = scrollbarRef.value
  if (!track) return
  const trackRect = track.getBoundingClientRect()
  setBoardScrollByThumbLeft(event.clientX - trackRect.left - thumbDragOffset)
}

function onThumbPointerUp(event) {
  if (!thumbDragging.value) return
  thumbDragging.value = false
  const thumb = thumbRef.value
  if (thumb && event?.pointerId != null && thumb.hasPointerCapture?.(event.pointerId)) {
    thumb.releasePointerCapture(event.pointerId)
  }
  window.removeEventListener('pointermove', onThumbPointerMove)
  window.removeEventListener('pointerup', onThumbPointerUp)
}

function onThumbPointerDown(event) {
  event.preventDefault()
  event.stopPropagation()
  const thumb = thumbRef.value
  if (!thumb) return
  thumbDragging.value = true
  const thumbRect = thumb.getBoundingClientRect()
  thumbDragOffset = event.clientX - thumbRect.left
  thumb.setPointerCapture?.(event.pointerId)
  window.addEventListener('pointermove', onThumbPointerMove)
  window.addEventListener('pointerup', onThumbPointerUp)
}

function onTrackPointerDown(event) {
  if (event.target !== scrollbarRef.value) return
  const track = scrollbarRef.value
  const thumb = thumbRef.value
  if (!track || !thumb) return
  const trackRect = track.getBoundingClientRect()
  const thumbWidth = thumb.offsetWidth
  setBoardScrollByThumbLeft(event.clientX - trackRect.left - thumbWidth / 2)
}

function onAction() {
}

onMounted(async () => {
  window.addEventListener('resize', updateThumb)
  try {
    const data = await crmApi.listColumns()
    columns.value = Array.isArray(data) ? data : []
    columnItemsModels.clear()
  } finally {
    loading.value = false
    await nextTick(updateThumb)
  }
})

onBeforeUnmount(() => {
  onDragEnd()
  onThumbPointerUp()
  cachedColumnBodies = null
  window.removeEventListener('resize', updateThumb)
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

.crm {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 20px 20px;
  box-sizing: border-box;
}

.crm__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--dvijok-text-secondary);
  font-size: 13px;
  line-height: 16px;
}

.crm__scrollbar {
  position: relative;
  flex-shrink: 0;
  width: 100%;
  height: 8px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 5px;
  box-sizing: border-box;
  cursor: pointer;
  touch-action: none;
}

.crm__scrollbar-thumb {
  position: absolute;
  top: -1px;
  left: 0;
  width: 60px;
  height: 8px;
  border-radius: 5px;
  background-color: var(--dvijok-blue-primary);
  box-sizing: border-box;
  cursor: grab;
  touch-action: none;
}

.crm__scrollbar-thumb--dragging {
  cursor: grabbing;
}

.crm__board-wrap {
  position: relative;
  flex: 1;
  min-height: 0;
  display: flex;
}

.crm__board {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 20px;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.crm__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  width: 50px;
  height: 50px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent url('/admin/icons/crm/nav-button-background.svg') center / 100% 100%
    no-repeat;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
  pointer-events: none;
  backdrop-filter: blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
}

.crm__nav--left {
  left: 6px;
  transform: translate(-6px, -50%);
}

.crm__nav--right {
  right: 6px;
  transform: translate(6px, -50%);
}

.crm__nav--visible {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(-50%);
}

.crm__nav-arrow {
  position: relative;
  z-index: 1;
}

.crm__column {
  flex: 0 0 280px;
  width: 280px;
  min-height: 0;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
}

.crm__column-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  flex-shrink: 0;
}

.crm__column-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.crm__column-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.crm__column-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 4px 15px;
  background-image: url('/admin/icons/crm/pill-background.svg');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.crm__column-pill-count {
  font-weight: 600;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-white);
}

.crm__column-sum {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-muted);
}

.crm__column-body {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  background-color: rgba(255, 255, 255, 0.22);
  background-image: url('/admin/icons/crm/column-body-background.svg');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  backdrop-filter: blur(28px) saturate(1.55);
  -webkit-backdrop-filter: blur(28px) saturate(1.55);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.65),
    inset 0 -1px 0 rgba(255, 255, 255, 0.28),
    inset 0 0 0 1px rgba(255, 255, 255, 0.42);
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.crm__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.crm__card {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px;
  border-radius: 10px;
  background: var(--dvijok-white);
  cursor: grab;
  user-select: none;
  box-sizing: border-box;
}

.crm__card:active {
  cursor: grabbing;
}

.crm__card--ghost {
  opacity: 0.45;
}

.crm__card--drag {
  opacity: 0.95;
}

.crm__card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.crm__card-number {
  margin: 0;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.crm__card-edit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;

  img {
    display: block;
    width: 16px;
    height: 16px;
  }
}

.crm__card-divider {
  width: 100%;
  height: 1px;
  background: var(--dvijok-text-secondary);
}

.crm__card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.crm__card-price {
  margin: 0;
  font-weight: 700;
  font-size: 13px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm__card-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-weight: 400;
  font-size: 11px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm__card-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.crm__card-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;

  img {
    display: block;
    width: 20px;
    height: 20px;
  }
}

.crm__card-services {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.crm__card-pills {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 5px;
}

.crm__card-pill {
  padding: 6px 10px;
  border-radius: 30px;
  background: var(--dvijok-muted);
  font-weight: 400;
  font-size: 9px;
  line-height: 11px;
  color: var(--dvijok-blue-primary);
}

.crm__card-masters {
  margin: 0;
  font-weight: 400;
  font-size: 10px;
  line-height: 14px;
  color: var(--dvijok-bg-dark);
}

.crm__card-masters-label {
  font-weight: 500;
}

.crm__card-dates {
  display: flex;
  flex-direction: column;
  font-weight: 400;
  font-size: 8px;
  line-height: 12px;
  color: var(--dvijok-bg-dark);

  p {
    margin: 0;
  }
}

.crm__card-dates-label {
  font-weight: 500;
}
</style>
