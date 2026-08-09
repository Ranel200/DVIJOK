<template>
  <div class="crm">
    <div v-if="loading" class="crm__loading" aria-live="polite">Загрузка доски…</div>
    <template v-else>
      <BaseScrollbar
        ref="boardScrollbarRef"
        track-only
        orientation="horizontal"
        :scroll-target="boardRef"
        @update:scrollable="boardScrollable = $event"
        @update:can-scroll-start="canScrollLeft = $event"
        @update:can-scroll-end="canScrollRight = $event"
      />

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

        <div ref="boardRef" class="crm__board">
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
                :force-fallback="true"
                :fallback-on-body="true"
                :scroll="false"
                @start="onDragStart"
                @end="onDragEnd"
              >
                <article
                  v-for="element in getColumnItemsModel(column).value"
                  :key="element.id"
                  class="crm__card"
                >
                  <div class="crm__card-top">
                    <h3 class="crm__card-number">{{ formatCrmOrderNumber(element.number) }}</h3>
                    <button
                      type="button"
                      class="crm__card-edit"
                      aria-label="Редактировать"
                      @pointerdown.stop
                      @click.stop="onEditCard(column, element)"
                    >
                      <img src="/admin/icons/services/edit.svg" alt="" />
                    </button>
                  </div>

                  <div class="crm__card-divider" aria-hidden="true" />

                  <div class="crm__card-body">
                    <p class="crm__card-price">{{ formatCrmMoney(element.amount) }} ₽</p>

                    <div class="crm__card-meta">
                      <span>{{ element.clientName }}</span>
                      <span class="crm_card-phone">{{ element.phone }}</span>
                    </div>

                    <div class="crm__card-meta">
                      <span>{{ element.carBrand }}</span>
                      <span>{{ element.plate }}</span>
                    </div>

                    <a
                      v-if="element.email"
                      class="crm__card-email"
                      :href="`mailto:${element.email}`"
                      @pointerdown.stop
                      @click.stop
                    >
                      {{ element.email }}
                    </a>

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
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseScrollbar from '@/components/ui/BaseScrollbar.vue'
import { formatCrmMoney, formatCrmOrderNumber, matchesCrmSearch } from '@/constants/crm.js'

const props = defineProps({
  columns: {
    type: Array,
    default: () => []
  },
  search: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit'])

const columnItemsModels = new Map()

function onEditCard(column, element) {
  emit('edit', {
    ...element,
    status: column.id
  })
}

function matchesSearch(element) {
  return matchesCrmSearch(element, props.search)
}

function getColumnItemsModel(column) {
  let model = columnItemsModels.get(column.id)
  if (!model) {
    model = computed({
      get: () => column.items.filter(matchesSearch),
      set: nextFiltered => {
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
const boardScrollbarRef = ref(null)
const boardScrollable = ref(false)
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const navLeftVisible = ref(false)
const navRightVisible = ref(false)

const NAV_EDGE_PX = 90
const EDGE_PX = 80
const MAX_SPEED = 14

let dragging = false
let pointerX = 0
let pointerY = 0
let autoScrollRaf = 0
let cachedColumnBodies = null

const columnStats = computed(() => {
  const stats = {}
  for (const column of props.columns) {
    const visible = column.items.filter(matchesSearch)
    const sum = visible.reduce((total, item) => total + (Number(item.amount) || 0), 0)
    stats[column.id] = {
      count: visible.length,
      sumFormatted: formatCrmMoney(sum)
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

function updateThumb() {
  boardScrollbarRef.value?.update()
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

function onDragStart(event) {
  dragging = true
  navLeftVisible.value = false
  navRightVisible.value = false
  const oe = event?.originalEvent
  if (oe?.clientX != null) {
    pointerX = oe.clientX
    pointerY = oe.clientY
  }
  cachedColumnBodies = Array.from(boardRef.value?.querySelectorAll('.crm__column-body') ?? [])
  window.addEventListener('pointermove', trackPointer, true)
  window.addEventListener('dragover', trackPointer, true)
  autoScrollRaf = requestAnimationFrame(tickAutoScroll)
}

function onDragEnd() {
  dragging = false
  cachedColumnBodies = null
  window.removeEventListener('pointermove', trackPointer, true)
  window.removeEventListener('dragover', trackPointer, true)
  if (autoScrollRaf) {
    cancelAnimationFrame(autoScrollRaf)
    autoScrollRaf = 0
  }
  nextTick(updateThumb)
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
  if (dragging) {
    navLeftVisible.value = false
    navRightVisible.value = false
    return
  }
  const wrap = boardWrapRef.value
  if (!wrap) return
  const rect = wrap.getBoundingClientRect()
  const x = event.clientX
  navLeftVisible.value = canScrollLeft.value && x - rect.left < NAV_EDGE_PX
  navRightVisible.value = canScrollRight.value && rect.right - x < NAV_EDGE_PX
}

watch(
  () => props.columns,
  () => {
    columnItemsModels.clear()
    nextTick(updateThumb)
  }
)

watch(
  () => props.loading,
  loading => {
    if (!loading) nextTick(updateThumb)
  }
)

onMounted(() => {
  nextTick(updateThumb)
})

onBeforeUnmount(() => {
  onDragEnd()
  cachedColumnBodies = null
})
</script>

<style scoped lang="scss">
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
  font-size: 16px;
  line-height: 19px;
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
  cursor: grabbing;
  box-shadow: 0 12px 28px rgba(11, 60, 186, 0.18);
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
  font-size: 14px;
  line-height: 17px;
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
  font-size: 14px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm__card-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-weight: 400;
  font-size: 14px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.crm__card-phone {
  font-size: 14px;
  line-height: 17px;
}

.crm__card-email {
  font-weight: 400;
  font-size: 14px;
  line-height: 15px;
  text-decoration: underline;
  color: #093095;
  cursor: pointer;
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
  font-size: 12px;
  line-height: 18px;
  color: var(--dvijok-bg-dark);
}

.crm__card-masters-label {
  font-weight: 500;
}

.crm__card-dates {
  display: flex;
  flex-direction: column;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-tab-inactive);

  p {
    margin: 0;
  }
}

.crm__card-dates-label {
  font-weight: 500;
}
</style>
