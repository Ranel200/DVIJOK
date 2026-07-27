<template>
  <div class="schedule-page">
    <AdminHeader
      :tabs="tabs"
      v-model:active-tab="activeTab"
      :action="action"
      @action-click="onAction"
    >
      <template #below>
        <div class="schedule-nav">
          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-light"
            size="lg"
            :icon-spacing="10"
            class="schedule-nav__btn schedule-nav__btn--prev"
            @click="onPrev"
          >
            <template #prepend>
              <ArrowIcon direction="left" />
            </template>
            {{ isCalendar ? 'Пред. Неделя' : 'Пред. Месяц' }}
          </BaseButton>

          <div
            class="schedule-nav__period-field"
            :class="{ 'schedule-nav__period-field--week': isCalendar }"
          >
            {{ periodLabel }}
          </div>

          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-light"
            size="lg"
            :icon-spacing="10"
            class="schedule-nav__btn schedule-nav__btn--next"
            @click="onNext"
          >
            {{ isCalendar ? 'След. Неделя' : 'След. Месяц' }}
            <template #append>
              <ArrowIcon direction="right" />
            </template>
          </BaseButton>

          <div class="schedule-legend">
            <div v-for="item in legendItems" :key="item.label" class="schedule-legend__item">
              <span class="schedule-legend__label">{{ item.label }}</span>
              <span
                class="schedule-legend__square"
                :style="{ background: item.bg, borderColor: item.border }"
              />
            </div>
          </div>
        </div>
      </template>
    </AdminHeader>

    <div class="schedule">
      <ScheduleCalendarTable ref="calendarTableRef" v-show="activeTab === 'calendar'" />
      <ScheduleStaffTable
        ref="staffTableRef"
        v-show="activeTab === 'staff'"
        :visible="activeTab === 'staff'"
      />
    </div>

    <ScheduleSettingsModal
      v-model="settingsOpen"
      :employees="settingsEmployees"
      @saved="onSettingsSaved"
    />

    <BaseModal v-model="savedOpen">
      <div class="schedule-saved">
        <h2 class="schedule-saved__title">График сохранен!</h2>
        <BaseButton color="blue1" size="lg" @click="savedOpen = false">Ок</BaseButton>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import ScheduleCalendarTable from '@/components/schedule/ScheduleCalendarTable.vue'
import ScheduleSettingsModal from '@/components/schedule/ScheduleSettingsModal.vue'
import ScheduleStaffTable from '@/components/schedule/ScheduleStaffTable.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { scheduleApi } from '@/api/index.js'
import { useScheduleFilterStore } from '@/stores/scheduleFilter.js'

const scheduleFilter = useScheduleFilterStore()

const tabs = [
  { label: 'Календарь', value: 'calendar' },
  { label: 'Сотрудники', value: 'staff' }
]
const activeTab = ref('calendar')

const isCalendar = computed(() => activeTab.value === 'calendar')

const CALENDAR_ACTION = { label: '+ Новый заказ' }
const STAFF_ACTION = { label: 'Настройки графика' }

const action = computed(() => (isCalendar.value ? CALENDAR_ACTION : STAFF_ACTION))

const periodLabel = computed(() =>
  isCalendar.value ? scheduleFilter.weekLabel : scheduleFilter.monthLabel
)

const CALENDAR_LEGEND = [
  { label: 'Сегодня', bg: 'var(--dvijok-choice-active)', border: 'var(--dvijok-today)' }
]
const STAFF_LEGEND = [
  { label: 'Сегодня', bg: 'var(--dvijok-choice-active)', border: 'var(--dvijok-today)' },
  { label: 'Рабочий день', bg: 'var(--dvijok-workday-bg)', border: 'var(--dvijok-workday)' },
  {
    label: 'Выходной день',
    bg: 'var(--dvijok-white)',
    border: 'var(--dvijok-text-secondary)'
  }
]

const legendItems = computed(() => (isCalendar.value ? CALENDAR_LEGEND : STAFF_LEGEND))

const settingsOpen = ref(false)
const savedOpen = ref(false)
const settingsEmployees = ref([])
const staffTableRef = ref(null)
const calendarTableRef = ref(null)

watch(settingsOpen, async open => {
  if (!open) return
  const data = await scheduleApi.employees({
    year: scheduleFilter.monthDate.getFullYear(),
    month: scheduleFilter.monthDate.getMonth()
  })
  settingsEmployees.value = data.map(item => ({
    id: item.id,
    name: item.name,
    role: item.role
  }))
})

function onPrev() {
  if (isCalendar.value) scheduleFilter.prevWeek()
  else scheduleFilter.prevMonth()
}

function onNext() {
  if (isCalendar.value) scheduleFilter.nextWeek()
  else scheduleFilter.nextMonth()
}

function onAction() {
  if (!isCalendar.value) {
    settingsOpen.value = true
  }
}

async function onSettingsSaved() {
  await Promise.all([staffTableRef.value?.reload?.(), calendarTableRef.value?.reload?.()])
  savedOpen.value = true
}

onMounted(() => scheduleFilter.resetToCurrent())
</script>

<style scoped lang="scss">
.schedule-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.schedule-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  width: 100%;
}

.schedule-nav__btn,
.schedule-nav__period-field {
  flex-shrink: 0;
}

.schedule-nav__btn--next {
  margin-right: auto;
}

.schedule-nav__period-field {
  display: flex;
  align-items: center;
  padding: 15px 15px;
  width: 156px;
  border: none;
  border-radius: 10px;
  background: var(--dvijok-white);
  box-shadow: inset 0 0 0 2px var(--dvijok-text-secondary);
  color: var(--dvijok-text-secondary);
  font-size: 14px;
  font-weight: 600;
  line-height: 17px;
  text-align: left;
  justify-content: flex-start;
  box-sizing: border-box;
}

.schedule-nav__period-field--week {
  width: auto;
  min-width: 196px;
  white-space: nowrap;
}

.schedule-legend {
  display: contents;
}

.schedule-legend__item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.schedule-legend__label {
  color: var(--dvijok-text-secondary);
  font-size: 13px;
  font-weight: 400;
  line-height: 16px;
}

.schedule-legend__square {
  width: 25px;
  height: 25px;
  border-radius: 5px;
  border: 1px solid;
}

.schedule {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.schedule-saved {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.schedule-saved__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}
</style>
