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
const publicCode = computed(() =>
  typeof route.params.referralCode === 'string' ? route.params.referralCode : ''
)
const isPublicBooking = computed(() => Boolean(publicCode.value))

const step = ref('branches')
const city = ref('Казань')
const branches = ref([])
const specialists = ref([])
const serviceOptions = ref([])
const timeSlots = ref([])
const availabilitySlots = ref([])
const availableDays = ref({})
const selectedBranchId = ref('')
const selectedSpecialistId = ref('any')
const selectedServiceId = ref('')
const selectedDate = ref('')
const selectedTime = ref('')
const successOpen = ref(false)
const backTarget = ref(null)
const GUEST_PHONE_STORAGE_KEY = 'dvijok_guest_phone'
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
  if (!isPublicBooking.value && selectedBranchId.value) query.branch = selectedBranchId.value
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
  if (!isPublicBooking.value) {
    selectedBranchId.value = typeof query.branch === 'string' ? query.branch : ''
  }
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

async function selectBranch(branch) {
  selectedBranchId.value = branch.id
  await Promise.all([loadBookingOptions(), loadSpecialists()])
  backTarget.value = null
  goToStep('menu')
}

async function onSubmitBooking(client) {
  const payload = {
    specialistId: selectedSpecialistId.value,
    serviceId: selectedServiceId.value,
    date: selectedDate.value,
    time: selectedTime.value,
    client
  }
  if (isPublicBooking.value) {
    await bookingApi.publicCreate(publicCode.value, payload)
    if (client.phone) {
      sessionStorage.setItem(GUEST_PHONE_STORAGE_KEY, client.phone)
    }
  } else {
    await bookingApi.create({
      branchId: selectedBranchId.value,
      ...payload
    })
  }
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
  const data = isPublicBooking.value
    ? await bookingApi.publicContext(publicCode.value)
    : await branchesApi.list()
  city.value = data.city
  branches.value = data.branches
  if (isPublicBooking.value) {
    selectedBranchId.value = branches.value[0]?.id || ''
    return
  }
  if (selectedBranchId.value && !branches.value.some(item => item.id === selectedBranchId.value)) {
    selectedBranchId.value = ''
  }
}

async function loadBookingOptions() {
  if (!selectedBranchId.value) return
  const data = isPublicBooking.value
    ? await bookingApi.publicOptions(publicCode.value)
    : await bookingApi.options({ branchId: selectedBranchId.value })
  serviceOptions.value = data.serviceOptions
  timeSlots.value = data.timeSlots
}

async function loadSpecialists() {
  if (!selectedBranchId.value) return
  const data = isPublicBooking.value
    ? await bookingApi.publicSpecialists(publicCode.value)
    : await bookingApi.specialists({ branchId: selectedBranchId.value })
  specialists.value = data.specialists
}

function syncTimeSlotsForDate() {
  if (!selectedDate.value) {
    timeSlots.value = []
    return
  }
  timeSlots.value = [
    ...new Set(
      availabilitySlots.value
        .filter(item => item.date === selectedDate.value)
        .map(item => item.time)
    )
  ]
  if (selectedTime.value && !timeSlots.value.includes(selectedTime.value)) {
    selectedTime.value = ''
  }
}

async function loadAvailability() {
  if (!selectedBranchId.value || !selectedServiceId.value) return
  const params = {
    year: monthCursor.value.getFullYear(),
    month: monthCursor.value.getMonth(),
    serviceId: selectedServiceId.value,
    specialistId: selectedSpecialistId.value
  }
  const data = isPublicBooking.value
    ? await bookingApi.publicAvailability(publicCode.value, params)
    : await bookingApi.availability({
        branchId: selectedBranchId.value,
        ...params
      })
  availableDays.value = data.days
  availabilitySlots.value = data.slots || []
  syncTimeSlotsForDate()
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

watch(selectedDate, syncTimeSlotsForDate)

watch([selectedServiceId, selectedSpecialistId], () => {
  if (step.value === 'datetime') loadAvailability()
})

watch(step, value => {
  if (value === 'datetime') loadAvailability()
})

onMounted(async () => {
  applyQuery(route.query)
  await loadBranches()
  if (selectedBranchId.value) {
    await Promise.all([loadBookingOptions(), loadSpecialists()])
  }
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
