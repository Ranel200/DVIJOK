<template>
  <div class="schedule-calendar" :style="columnVars">
    <div class="schedule-calendar__panel">
      <div class="schedule-calendar__table-wrap">
        <div
          v-if="todayIndex >= 0"
          class="schedule-calendar__today-overlay"
          :style="gridTemplateStyle"
          aria-hidden="true"
        >
          <div class="schedule-calendar__today-bg" :style="{ gridColumn: todayIndex + 2 }" />
        </div>

        <div class="schedule-calendar__grid" :style="gridTemplateStyle">
          <div class="schedule-calendar__time-head" />
          <div
            v-for="day in weekDays"
            :key="`head-${day.date}`"
            class="schedule-calendar__day-head"
          >
            {{ day.label }}
          </div>

          <template v-for="(slot, timeIndex) in timeRows" :key="slot.time">
            <div class="schedule-calendar__time" :style="{ gridRow: `span ${slot.rows.length}` }">
              {{ slot.time }}
            </div>

            <template v-for="(row, rowIndex) in slot.rows" :key="`${slot.time}-${row.employeeId}`">
              <div
                v-for="block in row.blocks"
                :key="block.id"
                class="schedule-calendar__day-cell"
                :class="{ 'schedule-calendar__day-cell--stacked': rowIndex > 0 }"
              >
                <div
                  class="schedule-calendar__block"
                  :class="`schedule-calendar__block--${block.status}`"
                  :style="blockStyle(block)"
                >
                  <span
                    v-if="block.status === 'unavailable'"
                    class="schedule-calendar__icon schedule-calendar__icon--lock"
                    aria-hidden="true"
                  />
                  <span
                    v-else-if="block.status === 'available'"
                    class="schedule-calendar__icon schedule-calendar__icon--unlock"
                    aria-hidden="true"
                  />
                  <template v-else>
                    <span class="schedule-calendar__brand">{{ block.brand }}</span>
                    <span class="schedule-calendar__plate">{{ block.plate }}</span>
                    <span class="schedule-calendar__meta">Клиент: {{ block.clientName }}</span>
                    <span class="schedule-calendar__meta schedule-calendar__meta--service">
                      Услуга: {{ block.serviceName }}
                    </span>
                  </template>
                </div>
              </div>
            </template>

            <div
              v-if="timeIndex < timeRows.length - 1"
              class="schedule-calendar__divider"
              aria-hidden="true"
            />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { scheduleApi } from '@/api/index.js'
import { useScheduleFilterStore } from '@/stores/scheduleFilter.js'
import { formatWeekdayDay } from '@/utils/formatDateRu.js'

const COL = {
  time: 48,
  timeGap: 20,
  dayMin: 96,
  dayPad: 5
}

// первая колонка: время + gap 20px минус padding первого дня
const columnVars = {
  '--schedule-cal-time': `${COL.time}px`,
  '--schedule-cal-time-col': `${COL.time + COL.timeGap - COL.dayPad}px`,
  '--schedule-cal-day-min': `${COL.dayMin}px`,
  '--schedule-cal-day-pad': `${COL.dayPad}px`
}

const gridTemplateStyle = {
  gridTemplateColumns:
    'var(--schedule-cal-time-col) repeat(7, minmax(var(--schedule-cal-day-min), 1fr))'
}

const scheduleFilter = useScheduleFilterStore()
const { weekStart } = storeToRefs(scheduleFilter)

const times = ref([])
const daysData = ref([])

const today = new Date()
today.setHours(0, 0, 0, 0)

const weekDays = computed(() =>
  daysData.value.map(day => {
    const date = new Date(`${day.date}T00:00:00`)
    return {
      date: day.date,
      label: formatWeekdayDay(date),
      isToday: date.getTime() === today.getTime(),
      slots: day.slots
    }
  })
)

const todayIndex = computed(() => weekDays.value.findIndex(day => day.isToday))

// ряды сотрудников внутри часа: только если есть смысл (не все lock)
const timeRows = computed(() =>
  times.value
    .map(time => {
      const employeeIds = []
      const seen = new Set()

      for (const day of weekDays.value) {
        for (const block of day.slots[time] || []) {
          if (!seen.has(block.employeeId)) {
            seen.add(block.employeeId)
            employeeIds.push(block.employeeId)
          }
        }
      }

      const rows = employeeIds
        .map(employeeId => ({
          employeeId,
          blocks: weekDays.value.map(day => {
            const found = (day.slots[time] || []).find(block => block.employeeId === employeeId)
            return (
              found || {
                id: `${employeeId}-${day.date}-${time}-empty`,
                employeeId,
                color: 'var(--dvijok-text-secondary)',
                status: 'unavailable'
              }
            )
          })
        }))
        .filter(row => row.blocks.some(block => block.status !== 'unavailable'))

      return { time, rows }
    })
    .filter(slot => slot.rows.length > 0)
)

function blockStyle(block) {
  if (block.status === 'unavailable') return null
  return {
    backgroundColor: `color-mix(in srgb, ${block.color} 22%, white)`,
    color: block.color
  }
}

function toWeekStartIso(date) {
  const d = date instanceof Date ? date : new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadCalendar() {
  const data = await scheduleApi.calendar({ weekStart: toWeekStartIso(weekStart.value) })
  times.value = data.times || []
  daysData.value = data.days || []
}

watch(weekStart, loadCalendar, { immediate: true })

defineExpose({ reload: loadCalendar })
</script>

<style scoped lang="scss">
.schedule-calendar {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 20px 20px;
}

.schedule-calendar__panel {
  flex: 1;
  min-height: 0;
  overflow: auto;
  box-sizing: border-box;
  background-color: var(--dvijok-white);
  border-radius: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.schedule-calendar__panel::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.schedule-calendar__table-wrap {
  position: relative;
  width: max-content;
  min-width: 100%;
  padding: 5px 10px;
  box-sizing: border-box;
}

.schedule-calendar__today-overlay,
.schedule-calendar__grid {
  display: grid;
  width: 100%;
  min-width: calc(var(--schedule-cal-time-col) + 7 * var(--schedule-cal-day-min));
}

.schedule-calendar__today-overlay {
  position: absolute;
  top: 5px;
  bottom: 5px;
  left: 10px;
  right: 10px;
  width: auto;
  min-width: 0;
  pointer-events: none;
  z-index: 0;
}

.schedule-calendar__today-bg {
  grid-row: 1 / -1;
  box-sizing: border-box;
  background-color: var(--dvijok-choice-active);
  border: 1px solid var(--dvijok-today);
  border-radius: 8px;
}

.schedule-calendar__grid {
  position: relative;
  z-index: 1;
}

.schedule-calendar__day-head {
  padding: 0 var(--schedule-cal-day-pad) 20px;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link-hover);
  text-align: center;
}

.schedule-calendar__time-head,
.schedule-calendar__time {
  width: var(--schedule-cal-time);
}

.schedule-calendar__time {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
  position: sticky;
  left: 10px;
  z-index: 2;
  background-color: var(--dvijok-white);
  box-shadow: -10px 0 0 var(--dvijok-white);
}

.schedule-calendar__day-cell {
  min-width: 0;
  padding: 10px var(--schedule-cal-day-pad);
}

.schedule-calendar__day-cell--stacked {
  padding-top: 0;
}

.schedule-calendar__block {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  min-height: 70px;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 8px;
  border: 1px solid;
}

.schedule-calendar__block--unavailable {
  align-items: center;
  background-color: var(--dvijok-white);
  border-color: var(--dvijok-text-secondary);
}

.schedule-calendar__block--available,
.schedule-calendar__block--busy {
  border-color: var(--dvijok-white);
}

.schedule-calendar__block--available {
  align-items: center;
}

.schedule-calendar__icon {
  display: block;
  flex-shrink: 0;
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  -webkit-mask-size: contain;
}

.schedule-calendar__icon--lock {
  width: 13px;
  height: 15px;
  background-color: var(--dvijok-text-secondary);
  mask-image: url('/admin/icons/schedule/lock.svg');
  -webkit-mask-image: url('/admin/icons/schedule/lock.svg');
}

.schedule-calendar__icon--unlock {
  width: 17px;
  height: 14px;
  background-color: currentColor;
  mask-image: url('/admin/icons/schedule/unlock.svg');
  -webkit-mask-image: url('/admin/icons/schedule/unlock.svg');
}

.schedule-calendar__brand,
.schedule-calendar__plate {
  font-weight: 700;
  font-size: 11px;
  line-height: 13px;
  color: inherit;
}

.schedule-calendar__meta {
  font-weight: 500;
  font-size: 10px;
  line-height: 12px;
  color: inherit;
}

.schedule-calendar__meta--service {
  font-weight: 400;
}

.schedule-calendar__divider {
  grid-column: 1 / -1;
  width: calc(100% + 20px);
  margin: 0 -10px;
  border: none;
  border-top: 1px dashed var(--dvijok-text-secondary);
  box-sizing: border-box;
}
</style>
