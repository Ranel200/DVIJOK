import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
  const currentDate = ref(new Date())

  const monthLabel = computed(
    () => `${MONTH_LABELS[currentDate.value.getMonth()]} ${currentDate.value.getFullYear()}`
  )

  function prevMonth() {
    const d = new Date(currentDate.value)
    d.setMonth(d.getMonth() - 1)
    currentDate.value = d
  }

  function nextMonth() {
    const d = new Date(currentDate.value)
    d.setMonth(d.getMonth() + 1)
    currentDate.value = d
  }

  function resetToCurrent() {
    currentDate.value = new Date()
  }

  return { currentDate, monthLabel, prevMonth, nextMonth, resetToCurrent }
})
