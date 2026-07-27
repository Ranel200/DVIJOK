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
            @click="scheduleFilter.prevMonth()"
          >
            <template #prepend>
              <ArrowIcon direction="left" />
            </template>
            Пред. Месяц
          </BaseButton>

          <div class="schedule-nav__month-field">{{ scheduleFilter.monthLabel }}</div>

          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-light"
            size="lg"
            :icon-spacing="10"
            class="schedule-nav__btn schedule-nav__btn--next"
            @click="scheduleFilter.nextMonth()"
          >
            След. Месяц
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
      <ScheduleStaffTable v-show="activeTab === 'staff'" :visible="activeTab === 'staff'" />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import ScheduleStaffTable from '@/components/schedule/ScheduleStaffTable.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import { useScheduleFilterStore } from '@/stores/scheduleFilter.js'

const scheduleFilter = useScheduleFilterStore()

const tabs = [
  { label: 'Календарь', value: 'calendar' },
  { label: 'Сотрудники', value: 'staff' }
]
const activeTab = ref('calendar')

const CALENDAR_ACTION = { label: '+ Новый заказ' }
const STAFF_ACTION = { label: 'Настройки графика' }

const action = computed(() => (activeTab.value === 'staff' ? STAFF_ACTION : CALENDAR_ACTION))

const CALENDAR_LEGEND = [
  { label: 'Сегодня', bg: 'var(--dvijok-choice-active)', border: 'var(--dvijok-today)' }
]
const STAFF_LEGEND = [
  { label: 'Сегодня', bg: 'var(--dvijok-choice-active)', border: 'var(--dvijok-today)' },
  { label: 'Рабочий день', bg: 'var(--dvijok-workday-bg)', border: 'var(--dvijok-workday)' },
  {
    label: 'Выходной день',
    bg: 'var(--dvijok-white)',
    border: 'var(--dvijok-weekend-muted)'
  }
]

const legendItems = computed(() => (activeTab.value === 'staff' ? STAFF_LEGEND : CALENDAR_LEGEND))

function onAction() {}

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
.schedule-nav__month-field {
  flex-shrink: 0;
}

.schedule-nav__btn--next {
  margin-right: auto;
}

.schedule-nav__month-field {
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
</style>
