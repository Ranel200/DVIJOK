<template>
  <div class="booking-flow">
    <div class="booking-flow__head">
      <div class="booking-flow__head-row">
        <div class="booking-flow__title-row">
          <button type="button" class="booking-flow__back" aria-label="Назад" @click="onBack">
            <ArrowIcon direction="left" :size="16" color="#182E5A" />
          </button>
          <h2 class="booking-flow__title">{{ stepTitle }}</h2>
        </div>
        <span class="booking-flow__step-label">Шаг {{ step }} из 3</span>
      </div>

      <div class="booking-flow__progress" aria-hidden="true">
        <span
          v-for="n in 3"
          :key="n"
          class="booking-flow__bar"
          :class="{ 'booking-flow__bar--active': n <= step }"
        />
      </div>
    </div>

    <template v-if="step === 1">
      <form class="booking-flow__form" @submit.prevent="goNext">
        <div class="booking-flow__field">
          <label class="booking-flow__label">Выберите услугу</label>
          <BaseSelect
            v-model="form.serviceId"
            :options="serviceOptions"
            placeholder="Услуга"
            block
          />
        </div>

        <div class="booking-flow__field">
          <label class="booking-flow__label">Выберите машину</label>
          <BaseSelect
            :model-value="form.carId"
            :options="carSelectOptions"
            placeholder="Машина"
            block
            @update:model-value="onCarChange"
          />
        </div>

        <div class="booking-flow__actions">
          <BaseButton color="blue1" size="sm" type="submit">Дальше</BaseButton>
        </div>
      </form>

      <AppBlock fixed-height class="booking-flow__promo">
        <div class="booking-promo">
          <img class="booking-promo__img" src="/client/icons/auth/img.svg" alt="" />
          <p class="booking-promo__text">Здесь могла бы быть ваша реклама</p>
        </div>
      </AppBlock>
    </template>

    <template v-else-if="step === 2">
      <div class="booking-flow__masters">
        <AppBlock
          v-for="master in masters"
          :key="master.id"
          compact
          :active="form.masterId === master.id"
          :title="master.name"
          :subtitle="master.subtitle"
          role="button"
          tabindex="0"
          class="booking-flow__master"
          @click="form.masterId = master.id"
          @keydown.enter.prevent="form.masterId = master.id"
        />
      </div>

      <div class="booking-flow__actions">
        <BaseButton color="blue1" size="sm" @click="goNext">Дальше</BaseButton>
      </div>
    </template>

    <template v-else>
      <div class="booking-flow__month">
        <button
          type="button"
          class="booking-flow__month-btn"
          aria-label="Предыдущий месяц"
          @click="shiftMonth(-1)"
        >
          <ChevronIcon direction="left" />
        </button>
        <span class="booking-flow__month-label">{{ monthLabel }}</span>
        <button
          type="button"
          class="booking-flow__month-btn"
          aria-label="Следующий месяц"
          @click="shiftMonth(1)"
        >
          <ChevronIcon direction="right" />
        </button>
      </div>

      <div class="booking-flow__calendar">
        <div
          v-for="day in WEEKDAYS"
          :key="day.label"
          class="booking-flow__weekday"
          :class="{ 'booking-flow__weekday--weekend': day.weekend }"
        >
          {{ day.label }}
        </div>

        <button
          v-for="(cell, index) in calendarCells"
          :key="`${monthCursor.getFullYear()}-${monthCursor.getMonth()}-${index}`"
          type="button"
          class="booking-flow__day"
          :class="dayClass(cell)"
          :aria-disabled="cell.day && !cell.available ? 'true' : undefined"
          @click="selectDate(cell)"
        >
          <template v-if="cell.day">
            <template v-if="cell.available">
              <span class="booking-flow__day-num">{{ cell.day }}</span>
              <span class="booking-flow__day-caption">{{ cell.caption }}</span>
            </template>
            <span v-else class="booking-flow__day-empty">—</span>
          </template>
        </button>
      </div>

      <h3 class="booking-flow__time-title">Выберите время</h3>

      <div class="booking-flow__times">
        <button
          v-for="time in timeSlots"
          :key="time"
          type="button"
          class="booking-flow__time"
          :class="{ 'booking-flow__time--active': form.time === time }"
          @click="form.time = time"
        >
          {{ time }}
        </button>
      </div>

      <div class="booking-flow__actions">
        <BaseButton color="blue1" size="sm" @click="onSubmit">Дальше</BaseButton>
      </div>
    </template>

    <BaseModal v-model="confirmOpen" persistent>
      <div class="booking-modal-card">
        <h2 class="booking-modal-card__title">Информация о записи:</h2>
        <div class="booking-modal-card__body">
          <p class="booking-modal-card__service">Сервис: “{{ serviceName }}”</p>
          <p class="booking-modal-card__datetime">{{ bookingDateTime }}</p>
          <p class="booking-modal-card__line">Услуга: {{ serviceLabel }}</p>
          <p class="booking-modal-card__line">Мастер: {{ masterLabel }}</p>
          <p class="booking-modal-card__line">Авто: {{ carLabel }}</p>
        </div>
      </div>

      <div class="booking-modal-actions">
        <BaseButton color="green" size="sm" block @click="onConfirmBooking">
          Подтвердить запись
        </BaseButton>
        <BaseButton
          color="blue2"
          size="sm"
          class="booking-modal-actions__secondary"
          @click="confirmOpen = false"
        >
          Вернуться
        </BaseButton>
      </div>
    </BaseModal>

    <BaseModal v-model="successOpen" persistent>
      <div class="booking-modal-success">
        <p class="booking-modal-success__title">Вы успешно записаны!</p>
        <p class="booking-modal-success__note">Ваша запись добавлена в раздел “Моё авто”</p>
      </div>

      <BaseButton color="blue2" size="sm" block @click="onGoToCar">Перейти</BaseButton>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { bookingApi } from '@/api/index.js'
import AppBlock from '@/components/ui/AppBlock.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import ChevronIcon from '@/components/ui/ChevronIcon.vue'

const router = useRouter()

const props = defineProps({
  serviceId: {
    type: String,
    default: ''
  },
  serviceName: {
    type: String,
    default: 'Автосервис'
  }
})

const emit = defineEmits(['close', 'complete', 'go-to-car'])

const STEP_TITLES = ['Выберите параметры', 'Выберите мастера', 'Выберите дату и время']

const WEEKDAYS = [
  { label: 'ПН', weekend: false },
  { label: 'ВТ', weekend: false },
  { label: 'СР', weekend: false },
  { label: 'ЧТ', weekend: false },
  { label: 'ПТ', weekend: false },
  { label: 'СБ', weekend: true },
  { label: 'ВС', weekend: true }
]

const MONTH_NAMES = [
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

const MONTH_NAMES_GEN = [
  'Января',
  'Февраля',
  'Марта',
  'Апреля',
  'Мая',
  'Июня',
  'Июля',
  'Августа',
  'Сентября',
  'Октября',
  'Ноября',
  'Декабря'
]

const ADD_CAR_VALUE = '__add_car__'

const serviceOptions = ref([])
const carOptions = ref([])
const masters = ref([])
const timeSlots = ref([])
const availableDays = ref({})

const step = ref(1)
const confirmOpen = ref(false)
const successOpen = ref(false)
const today = new Date()
today.setHours(0, 0, 0, 0)

const monthCursor = ref(new Date(today.getFullYear(), today.getMonth(), 1))

const form = reactive({
  serviceId: '',
  carId: '',
  masterId: 'any',
  date: '',
  time: ''
})

const stepTitle = computed(() => STEP_TITLES[step.value - 1])

const monthLabel = computed(() => MONTH_NAMES[monthCursor.value.getMonth()])

const carSelectOptions = computed(() => [
  { value: ADD_CAR_VALUE, label: '+ Добавить машину' },
  ...carOptions.value
])

const serviceLabel = computed(
  () => serviceOptions.value.find(item => item.value === form.serviceId)?.label || '—'
)

const carLabel = computed(
  () => carOptions.value.find(item => item.value === form.carId)?.label || '—'
)

const masterLabel = computed(
  () => masters.value.find(item => item.id === form.masterId)?.name || '—'
)

const bookingDateTime = computed(() => {
  if (!form.date || !form.time) return '—'
  const [, month, day] = form.date.split('-').map(Number)
  return `${day} ${MONTH_NAMES_GEN[month - 1].toLowerCase()} ${form.time}`
})

const calendarCells = computed(() => {
  const year = monthCursor.value.getFullYear()
  const month = monthCursor.value.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7
  const monthGen = MONTH_NAMES_GEN[month]
  const cells = []

  for (let i = 0; i < firstWeekday; i += 1) {
    cells.push({ day: null, available: false, iso: '', caption: '' })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day)
    const iso = toIso(date)
    const isToday = iso === toIso(today)
    const isPast = date < today
    const available = !isPast && Boolean(availableDays.value[day])
    cells.push({
      day,
      iso,
      available: available || isToday,
      caption: isToday ? 'Сегодня' : monthGen.slice(0, 3),
      isToday
    })
  }

  while (cells.length % 7 !== 0) {
    cells.push({ day: null, available: false, iso: '', caption: '' })
  }

  return cells
})

function toIso(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function dayClass(cell) {
  if (!cell.day) return 'booking-flow__day--spacer'
  if (!cell.available) return 'booking-flow__day--unavailable'
  return {
    'booking-flow__day--today': cell.isToday,
    'booking-flow__day--available': !cell.isToday,
    'booking-flow__day--selected': cell.iso === form.date
  }
}

function selectDate(cell) {
  if (!cell.available || !cell.iso) return
  form.date = cell.iso
}

function shiftMonth(delta) {
  const next = new Date(monthCursor.value.getFullYear(), monthCursor.value.getMonth() + delta, 1)
  monthCursor.value = next
}

function onBack() {
  if (step.value === 1) {
    emit('close')
    return
  }
  step.value -= 1
}

function onAddCar() {
  router.push({ name: 'car-create' })
}

function onCarChange(value) {
  if (value === ADD_CAR_VALUE) {
    onAddCar()
    return
  }
  form.carId = value
}

function goNext() {
  if (step.value < 3) step.value += 1
}

function onSubmit() {
  confirmOpen.value = true
}

async function onConfirmBooking() {
  await bookingApi.create({
    shopId: props.serviceId,
    shopName: props.serviceName,
    ...form
  })
  confirmOpen.value = false
  successOpen.value = true
}

function onGoToCar() {
  successOpen.value = false
  emit('complete', { shopId: props.serviceId, shopName: props.serviceName, ...form })
  emit('go-to-car')
}

async function loadOptions() {
  const data = await bookingApi.options({ shopId: props.serviceId })
  serviceOptions.value = data.serviceOptions
  carOptions.value = data.carOptions
  masters.value = data.masters
  timeSlots.value = data.timeSlots
  if (!form.masterId && data.masters[0]) {
    form.masterId = data.masters[0].id
  }
}

async function loadAvailability() {
  const data = await bookingApi.availability({
    shopId: props.serviceId,
    year: monthCursor.value.getFullYear(),
    month: monthCursor.value.getMonth()
  })
  availableDays.value = data.days
}

watch(monthCursor, () => {
  loadAvailability()
})

onMounted(async () => {
  await Promise.all([loadOptions(), loadAvailability()])
})
</script>

<style scoped lang="scss">
@use '../../css/glass' as glass;

.booking-flow {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
}

.booking-flow__head {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.booking-flow__head-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.booking-flow__title-row {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 30px;
  min-width: 0;
}

.booking-flow__back {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.booking-flow__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.booking-flow__step-label {
  flex-shrink: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.booking-flow__progress {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  height: 10px;
}

.booking-flow__bar {
  flex: 1;
  height: 10px;
  border-radius: 100px;
  background: var(--dvijok-white);
}

.booking-flow__bar--active {
  background: var(--dvijok-blue-primary);
}

.booking-flow__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.booking-flow__field {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.booking-flow__label {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.booking-flow__actions {
  display: flex;
  justify-content: flex-end;
}

.booking-flow__promo {
  justify-content: center;
  align-items: center;
}

.booking-promo {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.booking-promo__img {
  display: block;
  width: 82px;
  height: 82px;
}

.booking-promo__text {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
  text-align: center;
}

.booking-flow__masters {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.booking-flow__master {
  cursor: pointer;
  text-align: left;
  width: 100%;
}

.booking-flow__month {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.booking-flow__month-btn {
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

.booking-flow__month-label {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.booking-flow__calendar {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px 5px;
  width: 100%;
}

.booking-flow__weekday {
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

.booking-flow__weekday--weekend {
  color: var(--dvijok-danger-strong);
}

.booking-flow__day {
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

.booking-flow__day--spacer {
  visibility: hidden;
  pointer-events: none;
}

.booking-flow__day--unavailable {
  border-color: var(--dvijok-text-secondary);
  background: var(--dvijok-white);
  color: var(--dvijok-text-secondary);
  cursor: default;
  pointer-events: none;
}

.booking-flow__day--available {
  border-color: var(--dvijok-workday);
  background: var(--dvijok-workday-bg);
  color: var(--dvijok-workday);
}

.booking-flow__day--available.booking-flow__day--selected {
  background: var(--dvijok-workday);
  color: var(--dvijok-workday-bg);
}

.booking-flow__day--today {
  border-color: var(--dvijok-blue-primary);
  background: var(--dvijok-choice-active);
  color: var(--dvijok-blue-primary);
}

.booking-flow__day--today.booking-flow__day--selected {
  background: var(--dvijok-blue-primary);
  color: var(--dvijok-choice-active);
}

.booking-flow__day-num,
.booking-flow__day-caption,
.booking-flow__day-empty {
  display: block;
  width: 100%;
}

.booking-flow__time-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.booking-flow__times {
  display: grid;
  grid-template-columns: repeat(3, max-content);
  gap: 10px 5px;
}

.booking-flow__time {
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

.booking-flow__time--active {
  padding: 9px 24px;
  border-color: var(--dvijok-blue-primary);
  background: var(--dvijok-choice-active);
  color: var(--dvijok-blue-primary);
}

.booking-modal-card {
  @include glass.glass-dark;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  box-sizing: border-box;
}

.booking-modal-card__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-modal-card__body {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.booking-modal-card__service {
  margin: 0;
  font-weight: 700;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.booking-modal-card__datetime {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-modal-card__line {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-white);
}

.booking-modal-success {
  display: flex;
  flex-direction: column;
  gap: 17px;
  width: 100%;
  text-align: center;
}

.booking-modal-success__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-modal-success__note {
  margin: 0;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.booking-modal-actions {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 20px;
  width: 100%;
}

.booking-modal-actions__secondary {
  align-self: flex-start;
  width: fit-content;
}
</style>
