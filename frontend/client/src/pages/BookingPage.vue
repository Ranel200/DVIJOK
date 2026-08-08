<template>
  <q-page class="booking-page">
    <BranchesStep
      v-if="step === 'branches'"
      :city="city"
      :title="branchesTitleText"
      :branches="branches"
      @select="selectBranch"
    />

    <MenuStep
      v-else-if="step === 'menu'"
      :branch="selectedBranch"
      :items="MENU_ITEMS"
      @navigate="next => openStep(next, { from: 'menu' })"
    />

    <SpecialistStep
      v-else-if="step === 'specialist'"
      v-model="selectedSpecialistId"
      :specialists="specialists"
      :branch-name="selectedBranch?.name || ''"
      :branch-address="selectedBranch?.address || ''"
      @back="goBack('menu')"
      @next="goNext('service')"
    />

    <ServiceStep
      v-else-if="step === 'service'"
      v-model="selectedServiceId"
      :options="serviceOptions"
      :branch-name="selectedBranch?.name || ''"
      :branch-address="selectedBranch?.address || ''"
      @back="goBack('specialist')"
      @next="goNext('datetime')"
    />

    <DatetimeStep
      v-else-if="step === 'datetime'"
      :date="selectedDate"
      :time="selectedTime"
      :month-label="monthLabel"
      :month-key="monthKey"
      :calendar-cells="calendarCells"
      :time-slots="timeSlots"
      :branch-name="selectedBranch?.name || ''"
      :branch-address="selectedBranch?.address || ''"
      @update:date="selectedDate = $event"
      @update:time="selectedTime = $event"
      @shift-month="shiftMonth"
      @back="goBack('service')"
      @next="goNext('details')"
    />

    <DetailsStep
      v-else-if="step === 'details'"
      :branch-name="selectedBranch?.name || ''"
      :branch-address="selectedBranch?.address || ''"
      :specialist-name="specialistName"
      :specialist-role="specialistRole"
      :specialist-avatar-color="specialistAvatarColor"
      :date-label="selectedDateLabel"
      :time-range="selectedTimeRange"
      :service-label="selectedServiceLabel"
      :service-price="formatPrice(selectedServicePrice)"
      @back="goBack('datetime')"
      @edit="next => openStep(next, { from: 'details' })"
      @submit="onSubmitBooking"
    />

    <BookingPowered v-if="step !== 'branches'" />

    <BookingSuccessModal v-model="successOpen" @cabinet="goToCabinet" @exit="onExit" />
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { branchesApi, bookingApi } from '@/api/index.js'
import {
  BOOKING_STEPS,
  buildCalendarCells,
  branchesTitle,
  formatDateLabel,
  formatPrice,
  formatTimeRange,
  MENU_ITEMS,
  MONTH_NAMES
} from '@/utils/booking.js'
import BookingPowered from '@/components/booking/BookingPowered.vue'
import BookingSuccessModal from '@/components/booking/BookingSuccessModal.vue'
import BranchesStep from '@/components/booking/BranchesStep.vue'
import DatetimeStep from '@/components/booking/DatetimeStep.vue'
import DetailsStep from '@/components/booking/DetailsStep.vue'
import MenuStep from '@/components/booking/MenuStep.vue'
import ServiceStep from '@/components/booking/ServiceStep.vue'
import SpecialistStep from '@/components/booking/SpecialistStep.vue'

const route = useRoute()
const router = useRouter()

const step = ref('branches')
const city = ref('Казань')
const branches = ref([])
const specialists = ref([])
const serviceOptions = ref([])
const timeSlots = ref([])
const availableDays = ref({})
const selectedBranchId = ref('')
const selectedSpecialistId = ref('any')
const selectedServiceId = ref('')
const selectedDate = ref('')
const selectedTime = ref('')
const successOpen = ref(false)
const backTarget = ref(null)
let syncingQuery = false

const today = new Date()
today.setHours(0, 0, 0, 0)
const monthCursor = ref(new Date(today.getFullYear(), today.getMonth(), 1))

const selectedBranch = computed(
  () => branches.value.find(item => item.id === selectedBranchId.value) || null
)

const selectedSpecialist = computed(() => {
  if (selectedSpecialistId.value === 'any') return null
  return specialists.value.find(item => item.id === selectedSpecialistId.value) || null
})

const specialistName = computed(() =>
  selectedSpecialist.value ? selectedSpecialist.value.name : 'Любой специалист'
)

const specialistRole = computed(() =>
  selectedSpecialist.value ? selectedSpecialist.value.role : 'Определяется автоматически'
)

const specialistAvatarColor = computed(
  () => selectedSpecialist.value?.avatarColor || 'var(--dvijok-accent-coral)'
)

const selectedService = computed(
  () => serviceOptions.value.find(item => item.value === selectedServiceId.value) || null
)

const selectedServiceLabel = computed(() => selectedService.value?.label || '—')
const selectedServicePrice = computed(() => selectedService.value?.price || 0)

const branchesTitleText = computed(() => branchesTitle(branches.value.length))
const monthLabel = computed(() => MONTH_NAMES[monthCursor.value.getMonth()])
const monthKey = computed(
  () => `${monthCursor.value.getFullYear()}-${monthCursor.value.getMonth()}`
)
const selectedDateLabel = computed(() => formatDateLabel(selectedDate.value))
const selectedTimeRange = computed(() => formatTimeRange(selectedTime.value))

const calendarCells = computed(() =>
  buildCalendarCells(monthCursor.value, availableDays.value, today)
)

function shiftMonth(delta) {
  monthCursor.value = new Date(
    monthCursor.value.getFullYear(),
    monthCursor.value.getMonth() + delta,
    1
  )
}

function buildQuery() {
  const query = { step: step.value }
  if (selectedBranchId.value) query.branch = selectedBranchId.value
  if (selectedSpecialistId.value) query.specialist = selectedSpecialistId.value
  if (selectedServiceId.value) query.service = selectedServiceId.value
  if (selectedDate.value) query.date = selectedDate.value
  if (selectedTime.value) query.time = selectedTime.value
  return query
}

async function syncQuery() {
  if (syncingQuery) return
  const query = buildQuery()
  const current = route.query
  const same =
    String(current.step || '') === String(query.step || '') &&
    String(current.branch || '') === String(query.branch || '') &&
    String(current.specialist || '') === String(query.specialist || '') &&
    String(current.service || '') === String(query.service || '') &&
    String(current.date || '') === String(query.date || '') &&
    String(current.time || '') === String(query.time || '')
  if (same) return
  syncingQuery = true
  try {
    await router.replace({ query })
  } finally {
    syncingQuery = false
  }
}

function applyQuery(query) {
  const nextStep = BOOKING_STEPS.has(query.step) ? query.step : 'branches'
  step.value = nextStep
  selectedBranchId.value = typeof query.branch === 'string' ? query.branch : ''
  selectedSpecialistId.value =
    typeof query.specialist === 'string' && query.specialist ? query.specialist : 'any'
  selectedServiceId.value = typeof query.service === 'string' ? query.service : ''
  selectedDate.value = typeof query.date === 'string' ? query.date : ''
  selectedTime.value = typeof query.time === 'string' ? query.time : ''
}

function goToStep(next) {
  if (next !== 'branches' && !selectedBranchId.value && next !== 'menu') {
    step.value = 'branches'
    return
  }
  step.value = next
}

function openStep(next, { from } = {}) {
  backTarget.value = from || null
  goToStep(next)
}

function goBack(fallback) {
  const target = backTarget.value || fallback
  backTarget.value = null
  goToStep(target)
}

function goNext(fallback) {
  if (backTarget.value === 'details') {
    const target = backTarget.value
    backTarget.value = null
    goToStep(target)
    return
  }
  backTarget.value = null
  goToStep(fallback)
}

function selectBranch(branch) {
  selectedBranchId.value = branch.id
  backTarget.value = null
  goToStep('menu')
}

async function onSubmitBooking(client) {
  await bookingApi.create({
    branchId: selectedBranchId.value,
    specialistId: selectedSpecialistId.value,
    serviceId: selectedServiceId.value,
    date: selectedDate.value,
    time: selectedTime.value,
    client
  })
  successOpen.value = true
}

function goToCabinet() {
  successOpen.value = false
  router.push({ name: 'home' })
}

function onExit() {
  successOpen.value = false
  router.push({ name: 'home' })
}

async function loadBranches() {
  const data = await branchesApi.list()
  city.value = data.city
  branches.value = data.branches
  if (selectedBranchId.value && !branches.value.some(item => item.id === selectedBranchId.value)) {
    selectedBranchId.value = ''
  }
}

async function loadBookingOptions() {
  const data = await bookingApi.options({ branchId: selectedBranchId.value })
  serviceOptions.value = data.serviceOptions
  timeSlots.value = data.timeSlots
}

async function loadSpecialists() {
  const data = await bookingApi.specialists({ branchId: selectedBranchId.value })
  specialists.value = data.specialists
}

async function loadAvailability() {
  const data = await bookingApi.availability({
    branchId: selectedBranchId.value,
    year: monthCursor.value.getFullYear(),
    month: monthCursor.value.getMonth()
  })
  availableDays.value = data.days
}

watch(
  [step, selectedBranchId, selectedSpecialistId, selectedServiceId, selectedDate, selectedTime],
  () => {
    syncQuery()
  }
)

watch(
  () => route.query,
  query => {
    if (syncingQuery) return
    applyQuery(query)
  }
)

watch(monthCursor, () => {
  if (step.value === 'datetime') loadAvailability()
})

watch(step, value => {
  if (value === 'datetime') loadAvailability()
})

onMounted(async () => {
  applyQuery(route.query)
  await Promise.all([loadBranches(), loadBookingOptions(), loadSpecialists()])
  if (step.value === 'datetime' || selectedDate.value) {
    await loadAvailability()
  }
  syncQuery()
})
</script>

<style scoped lang="scss">
.booking-page {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 100%;
  padding: 25px 15px;
  box-sizing: border-box;
}
</style>
