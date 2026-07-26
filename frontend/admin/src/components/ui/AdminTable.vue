<template>
  <div class="admin-table">
    <div class="admin-table__head">
      <table class="admin-table__table">
        <colgroup>
          <col
            v-for="(style, index) in columnStyles"
            :key="`head-${columns[index].key}`"
            :style="style"
          />
        </colgroup>
        <thead>
          <tr>
            <slot name="head" />
          </tr>
        </thead>
      </table>
    </div>
    <div class="admin-table__list">
      <table class="admin-table__table">
        <colgroup>
          <col
            v-for="(style, index) in columnStyles"
            :key="`body-${columns[index].key}`"
            :style="style"
          />
        </colgroup>
        <tbody>
          <template v-if="loading">
            <tr
              v-for="row in skeletonRowCount"
              :key="`loading-${row}`"
              class="admin-table__row admin-table__row--loading"
            >
              <td
                v-for="col in columns"
                :key="`${row}-${col.key}`"
                class="admin-table__cell"
                :class="{ 'admin-table__cell--check': col.key === 'check' }"
              >
                <div
                  class="admin-table__bg"
                  :class="{ 'admin-table__bg--check': col.key === 'check' }"
                />
              </td>
            </tr>
          </template>
          <template v-else>
            <slot />
            <tr v-if="empty">
              <td :colspan="columns.length" class="admin-table__empty">
                {{ emptyText }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <div v-if="$slots.footer" class="admin-table__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  empty: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: 'Нет данных'
  },
  loading: {
    type: Boolean,
    default: false
  },
  skeletonRowCount: {
    type: Number,
    default: 6
  }
})

const columnStyles = computed(() => {
  let fixedPx = 0
  let frSum = 0
  const parsed = props.columns.map(col => {
    const width = col.width
    if (typeof width === 'string' && width.endsWith('fr')) {
      const fr = Number.parseFloat(width)
      frSum += fr
      return { type: 'fr', fr }
    }
    if (typeof width === 'string' && width.endsWith('px')) {
      fixedPx += Number.parseFloat(width)
      return { type: 'fixed', width }
    }
    if (width) return { type: 'raw', width }
    return { type: 'auto' }
  })

  return parsed.map(col => {
    if (col.type === 'fr' && frSum > 0) {
      return { width: `calc((100% - ${fixedPx}px) * ${col.fr / frSum})` }
    }
    if (col.type === 'fixed' || col.type === 'raw') return { width: col.width }
    return undefined
  })
})
</script>

<style scoped lang="scss">
.admin-table {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 20px 20px;
}

.admin-table__head {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.admin-table__list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background-color: var(--dvijok-white);
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.admin-table__list::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.admin-table__table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

.admin-table__footer {
  margin-top: 40px;
  display: flex;
  justify-content: flex-start;
  flex-shrink: 0;
}

:slotted(.admin-table__row) {
  border-bottom: 1px solid var(--dvijok-text-secondary);
}

:slotted(.admin-table__row:last-child) {
  border-bottom: none;
}

:slotted(.admin-table__th),
:slotted(.admin-table__cell) {
  padding: 9px 0;
  text-align: left;
  vertical-align: middle;
  box-sizing: border-box;
}

:slotted(.admin-table__th--check),
:slotted(.admin-table__cell--check) {
  padding-left: 19px;
}

:slotted(.admin-table__th) {
  font-weight: 700;
  font-size: 12px;
  line-height: 19px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

:slotted(.admin-table__title) {
  font-weight: 700;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

:slotted(.admin-table__desc) {
  margin-top: 4px;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

:slotted(.admin-table__text) {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
}

.admin-table__empty {
  padding: 20px 19px;
  text-align: center;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.admin-table__row--loading {
  border-bottom: 1px solid var(--dvijok-text-secondary);
}

.admin-table__row--loading:last-child {
  border-bottom: none;
}

.admin-table__cell {
  padding: 9px 0;
  text-align: left;
  vertical-align: middle;
  box-sizing: border-box;
}

.admin-table__cell--check {
  padding-left: 19px;
}

.admin-table__bg {
  width: 70%;
  height: 12px;
  border-radius: 4px;
  background: var(--dvijok-muted);
  animation: admin-table-bg-pulse 1.2s ease-in-out infinite;
}

.admin-table__bg--check {
  width: 16px;
  height: 16px;
}

@keyframes admin-table-bg-pulse {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}
</style>
