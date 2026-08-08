<template>
  <div class="datetime-step">
    <BookingStepHead :name="branchName" :address="branchAddress" @back="emit('back')" />

    <h2 class="booking-step-title">Выбрать дату</h2>

    <div class="datetime-step__month">
      <button
        type="button"
        class="datetime-step__month-btn"
        aria-label="Предыдущий месяц"
        @click="emit('shift-month', -1)"
      >
        <ChevronIcon direction="left" />
      </button>
      <span class="datetime-step__month-label">{{ monthLabel }}</span>
      <button
        type="button"
        class="datetime-step__month-btn"
        aria-label="Следующий месяц"
        @click="emit('shift-month', 1)"
      >
        <ChevronIcon direction="right" />
      </button>
    </div>

    <div class="datetime-step__calendar">
      <div
        v-for="day in WEEKDAYS"
        :key="day.label"
        class="datetime-step__weekday"
        :class="{ 'datetime-step__weekday--weekend': day.weekend }"
      >
        {{ day.label }}
      </div>

      <button
        v-for="(cell, index) in calendarCells"
        :key="`${monthKey}-${index}`"
        type="button"
        class="datetime-step__day"
        :class="dayClass(cell, date, 'datetime-step')"
        :aria-disabled="cell.day && !cell.available ? 'true' : undefined"
        @click="onSelectDate(cell)"
      >
        <template v-if="cell.day">
          <template v-if="cell.available">
            <span class="datetime-step__day-num">{{ cell.day }}</span>
            <span class="datetime-step__day-caption">{{ cell.caption }}</span>
          </template>
          <span v-else class="datetime-step__day-empty">—</span>
        </template>
      </button>
    </div>

    <h3 class="datetime-step__time-title">Выберите время</h3>

    <div class="datetime-step__times">
      <button
        v-for="slot in timeSlots"
        :key="slot"
        type="button"
        class="datetime-step__time"
        :class="{ 'datetime-step__time--active': time === slot }"
        @click="emit('update:time', slot)"
      >
        {{ slot }}
      </button>
    </div>

    <BaseButton color="blue1" size="sm" block @click="emit('next')">Далее</BaseButton>
  </div>
</template>

<script setup>
import { dayClass, WEEKDAYS } from '@/utils/booking.js'
import BaseButton from '@/components/ui/BaseButton.vue'
import BookingStepHead from '@/components/booking/BookingStepHead.vue'
import ChevronIcon from '@/components/ui/ChevronIcon.vue'

defineProps({
  date: {
    type: String,
    default: ''
  },
  time: {
    type: String,
    default: ''
  },
  monthLabel: {
    type: String,
    default: ''
  },
  monthKey: {
    type: String,
    default: ''
  },
  calendarCells: {
    type: Array,
    default: () => []
  },
  timeSlots: {
    type: Array,
    default: () => []
  },
  branchName: {
    type: String,
    default: ''
  },
  branchAddress: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:date', 'update:time', 'shift-month', 'back', 'next'])

function onSelectDate(cell) {
  if (!cell.available || !cell.iso) return
  emit('update:date', cell.iso)
}
</script>

<style scoped lang="scss">
.datetime-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.datetime-step__month {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.datetime-step__month-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 20px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.datetime-step__month-label {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.datetime-step__calendar {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px 5px;
  width: 100%;
}

.datetime-step__weekday {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 7px 0;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
  text-align: center;
}

.datetime-step__weekday--weekend {
  color: var(--dvijok-danger-strong);
}

.datetime-step__day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 10px 0;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  text-align: center;
}

.datetime-step__day--spacer {
  visibility: hidden;
  pointer-events: none;
}

.datetime-step__day--unavailable {
  border-color: var(--dvijok-text-secondary);
  background: var(--dvijok-white);
  color: var(--dvijok-text-secondary);
  cursor: default;
  pointer-events: none;
}

.datetime-step__day--available {
  border-color: var(--dvijok-workday);
  background: var(--dvijok-workday-bg);
  color: var(--dvijok-workday);
}

.datetime-step__day--available.datetime-step__day--selected {
  background: var(--dvijok-workday);
  color: var(--dvijok-workday-bg);
}

.datetime-step__day--today {
  border-color: var(--dvijok-blue-primary);
  background: var(--dvijok-choice-active);
  color: var(--dvijok-blue-primary);
}

.datetime-step__day--today.datetime-step__day--selected {
  background: var(--dvijok-blue-primary);
  color: var(--dvijok-choice-active);
}

.datetime-step__day-num,
.datetime-step__day-caption,
.datetime-step__day-empty {
  display: block;
  width: 100%;
}

.datetime-step__time-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.datetime-step__times {
  display: grid;
  grid-template-columns: repeat(3, max-content);
  gap: 10px 5px;
}

.datetime-step__time {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 25px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 50px;
  background: var(--dvijok-white);
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.datetime-step__time--active {
  padding: 9px 24px;
  border-color: var(--dvijok-blue-primary);
  background: var(--dvijok-choice-active);
  color: var(--dvijok-blue-primary);
}
</style>
