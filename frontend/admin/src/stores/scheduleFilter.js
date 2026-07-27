import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { formatWeekRange, startOfWeek } from '@/utils/formatDateRu.js'

const MONTH_LABELS = [
  'Январь',
  'Февраль',
  'Март',
  'Апрель',
  'Май',
  'Июнь',
  'Июль',
  'Август',
  'Сентябрь',
  'Октябрь',
  'Ноябрь',
  'Декабрь'
]

export const useScheduleFilterStore = defineStore('scheduleFilter', () => {
  const monthDate = ref(new Date())
  const weekDate = ref(new Date())

  const monthLabel = computed(
    () => `${MONTH_LABELS[monthDate.value.getMonth()]} ${monthDate.value.getFullYear()}`
  )

  const weekLabel = computed(() => formatWeekRange(weekDate.value))

  const weekStart = computed(() => startOfWeek(weekDate.value))

  function prevMonth() {
    const d = new Date(monthDate.value)
    d.setMonth(d.getMonth() - 1)
    monthDate.value = d
  }

  function nextMonth() {
    const d = new Date(monthDate.value)
    d.setMonth(d.getMonth() + 1)
    monthDate.value = d
  }

  function prevWeek() {
    const d = new Date(weekDate.value)
    d.setDate(d.getDate() - 7)
    weekDate.value = d
  }

  function nextWeek() {
    const d = new Date(weekDate.value)
    d.setDate(d.getDate() + 7)
    weekDate.value = d
  }

  function resetToCurrent() {
    const now = new Date()
    monthDate.value = now
    weekDate.value = new Date(now)
  }

  return {
    monthDate,
    weekDate,
    monthLabel,
    weekLabel,
    weekStart,
    prevMonth,
    nextMonth,
    prevWeek,
    nextWeek,
    resetToCurrent
  }
})
