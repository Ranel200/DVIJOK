<template>
  <BaseModal v-model="open" size="drawer" padding="40px 15px 60px 30px" hide-close>
    <div class="schedule-settings">
      <h2 class="schedule-settings__title">Настройки графика</h2>

      <div class="schedule-settings__form">
        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Шаг записи</span>
          <BaseChoice
            v-model="draft.slotStep"
            class="schedule-settings__choice schedule-settings__choice--step"
            :options="slotStepOptions"
            shape="rounded"
            gap="10px"
          />
          <div v-if="draft.slotStep === 'custom'" class="schedule-settings__field schedule-settings__field--nested">
            <span class="schedule-settings__label">Введите свой вариант</span>
            <BaseInput
              v-model="draft.customSlotStep"
              class="schedule-settings__custom-step"
              placeholder="1 минута"
              mask="###"
              block
            />
          </div>
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Рабочее время</span>
          <div
            v-for="(period, index) in draft.workPeriods"
            :key="`work-${index}`"
            class="schedule-settings__row"
          >
            <div class="schedule-settings__time-row">
              <BaseInput v-model="period.start" mask="##:##" block />
              <span class="schedule-settings__time-sep" aria-hidden="true" />
              <BaseInput v-model="period.end" mask="##:##" block />
            </div>
            <button
              type="button"
              class="schedule-settings__remove"
              :class="{ 'schedule-settings__remove--active': index > 0 }"
              :disabled="index === 0"
              aria-label="Удалить рабочее время"
              @click="removeWorkPeriod(index)"
            />
          </div>
          <button type="button" class="schedule-settings__add" @click="addWorkPeriod">
            + Добавить рабочее время
          </button>
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Перерывы</span>
          <div
            v-for="(breakItem, index) in draft.breaks"
            :key="`break-${index}`"
            class="schedule-settings__row"
          >
            <div class="schedule-settings__time-row">
              <BaseInput v-model="breakItem.start" mask="##:##" block />
              <span class="schedule-settings__time-sep" aria-hidden="true" />
              <BaseInput v-model="breakItem.end" mask="##:##" block />
            </div>
            <button
              type="button"
              class="schedule-settings__remove schedule-settings__remove--active"
              aria-label="Удалить перерыв"
              @click="removeBreak(index)"
            />
          </div>
          <button type="button" class="schedule-settings__add" @click="addBreak">
            + Добавить перерыв
          </button>
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Дни недели</span>
          <BaseChoice
            v-model="draft.workDays"
            class="schedule-settings__choice schedule-settings__choice--weekdays schedule-settings__weekdays"
            :options="weekdayOptions"
            shape="rounded"
            multiple
            gap="10px"
          />
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Применить к</span>
          <div
            v-for="(employeeId, index) in draft.employeeIds"
            :key="`employee-${index}`"
            class="schedule-settings__row"
          >
            <BaseSelect
              v-model="draft.employeeIds[index]"
              :options="employeeOptions"
              placeholder="Все сотрудники"
              block
            />
            <button
              type="button"
              class="schedule-settings__remove"
              :class="{ 'schedule-settings__remove--active': index > 0 }"
              :disabled="index === 0"
              aria-label="Удалить сотрудника"
              @click="removeEmployee(index)"
            />
          </div>
          <button type="button" class="schedule-settings__add" @click="addEmployee">
            + Добавить сотрудника
          </button>
        </div>
      </div>

      <p v-if="formError" class="schedule-settings__error">{{ formError }}</p>

      <div class="schedule-settings__actions">
        <BaseButton
          color="blue1"
          scheme="outlinedWhite-solid-outlinedWhite"
          size="lg"
          @click="close"
        >
          Отмена
        </BaseButton>
        <BaseButton color="blue1" size="lg" :loading="saving" @click="onSave">
          Сохранить
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import { scheduleApi } from '@/api/index.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  employees: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const saving = ref(false)
const formError = ref('')

const slotStepOptions = [
  { value: 120, label: '120 мин' },
  { value: 60, label: '60 мин' },
  { value: 30, label: '30 мин' },
  { value: 15, label: '15 мин' },
  { value: 'custom', label: 'Другое значение' }
]

const weekdayOptions = [
  { label: 'Пн', value: 1 },
  { label: 'Вт', value: 2 },
  { label: 'Ср', value: 3 },
  { label: 'Чт', value: 4 },
  { label: 'Пт', value: 5 },
  { label: 'Сб', value: 6 },
  { label: 'Вс', value: 0 }
]

const draft = reactive(createEmptyDraft())

const open = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

const employeeOptions = computed(() => [
  { value: 'all', label: 'Все сотрудники' },
  ...props.employees.map(employee => ({
    value: employee.id,
    label: `${employee.name} — ${employee.role}`
  }))
])

watch(
  () => props.modelValue,
  openValue => {
    if (!openValue) return
    resetDraft()
    formError.value = ''
  }
)

function createEmptyDraft() {
  return {
    slotStep: 60,
    customSlotStep: '',
    workPeriods: [{ start: '09:00', end: '18:00' }],
    breaks: [],
    workDays: [1, 2, 3, 4, 5],
    employeeIds: ['all']
  }
}

function resetDraft() {
  const next = createEmptyDraft()
  draft.slotStep = next.slotStep
  draft.customSlotStep = next.customSlotStep
  draft.workPeriods.splice(
    0,
    draft.workPeriods.length,
    ...next.workPeriods.map(item => ({ ...item }))
  )
  draft.breaks.splice(0, draft.breaks.length)
  draft.workDays.splice(0, draft.workDays.length, ...next.workDays)
  draft.employeeIds.splice(0, draft.employeeIds.length, ...next.employeeIds)
}

function addWorkPeriod() {
  draft.workPeriods.push({ start: '', end: '' })
  formError.value = ''
}

function removeWorkPeriod(index) {
  if (index === 0) return
  draft.workPeriods.splice(index, 1)
  formError.value = ''
}

function addBreak() {
  draft.breaks.push({ start: '', end: '' })
  formError.value = ''
}

function removeBreak(index) {
  draft.breaks.splice(index, 1)
  formError.value = ''
}

function addEmployee() {
  draft.employeeIds.push('all')
  formError.value = ''
}

function removeEmployee(index) {
  if (index === 0) return
  draft.employeeIds.splice(index, 1)
  formError.value = ''
}

function close() {
  open.value = false
}

function parseTimeMinutes(value) {
  if (!/^\d{2}:\d{2}$/.test(value || '')) return null
  const [hours, minutes] = value.split(':').map(Number)
  if (hours > 23 || minutes > 59) return null
  return hours * 60 + minutes
}

function resolveSlotStep() {
  if (draft.slotStep === 'custom') {
    const minutes = Number(draft.customSlotStep)
    if (!Number.isInteger(minutes) || minutes <= 0) return null
    return minutes
  }
  return draft.slotStep
}

function validateTimeRange(item, { invalid, order }) {
  const start = parseTimeMinutes(item.start)
  const end = parseTimeMinutes(item.end)
  if (start == null || end == null) {
    return invalid
  }
  if (start >= end) {
    return order
  }
  return { start, end }
}

function validate() {
  if (resolveSlotStep() == null) {
    return 'Укажите корректный шаг записи в минутах'
  }

  const periods = []
  for (const item of draft.workPeriods) {
    const result = validateTimeRange(item, {
      invalid: 'Укажите корректное рабочее время (ЧЧ:ММ)',
      order: 'В рабочем времени начало должно быть меньше окончания'
    })
    if (typeof result === 'string') return result
    periods.push(result)
  }

  if (!draft.workDays.length) {
    return 'Выберите хотя бы один рабочий день'
  }

  for (const item of draft.breaks) {
    const result = validateTimeRange(item, {
      invalid: 'Укажите корректное время перерыва (ЧЧ:ММ)',
      order: 'В перерыве время начала должно быть меньше окончания'
    })
    if (typeof result === 'string') return result
    const inside = periods.some(period => result.start >= period.start && result.end <= period.end)
    if (!inside) {
      return 'Перерыв должен быть внутри рабочего времени'
    }
  }

  if (!draft.employeeIds.length) {
    return 'Выберите хотя бы одного сотрудника'
  }

  return ''
}

async function onSave() {
  const error = validate()
  if (error) {
    formError.value = error
    return
  }

  formError.value = ''
  saving.value = true
  try {
    const firstPeriod = draft.workPeriods[0]
    // Новая структура (пока без бэка):
    // await scheduleApi.saveSettings({
    //   slotStep: resolveSlotStep(),
    //   workPeriods: draft.workPeriods.map(item => ({ start: item.start, end: item.end })),
    //   breaks: draft.breaks.map(item => ({ start: item.start, end: item.end })),
    //   workDays: [...draft.workDays],
    //   employeeIds: [...draft.employeeIds]
    // })
    await scheduleApi.saveSettings({
      start: firstPeriod.start,
      end: firstPeriod.end,
      breaks: draft.breaks.map(item => ({ start: item.start, end: item.end })),
      workDays: [...draft.workDays],
      employeeId: draft.employeeIds[0]
    })
    open.value = false
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.schedule-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  height: 100%;
}

.schedule-settings__title {
  margin: 0;
  font-weight: 700;
  font-size: 24px;
  line-height: 36px;
  color: var(--dvijok-bg-dark);
}

.schedule-settings__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  min-height: 0;
  overflow: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.schedule-settings__field {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.schedule-settings__label {
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  line-height: 16px;
  text-align: left;
}

.schedule-settings__choice--step :deep(.base-choice__option) {
  padding: 6px;
}

.schedule-settings__choice--weekdays :deep(.base-choice__option) {
  padding: 6px 14px;
}

.schedule-settings__form :deep(.base-input .q-field__control) {
  padding: 7px;
}

.schedule-settings__form :deep(.base-input .q-field__native) {
  text-align: center;
}

.schedule-settings__row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.schedule-settings__row > :deep(.base-select) {
  flex: 1;
  min-width: 0;
}

.schedule-settings__remove {
  flex-shrink: 0;
  width: 13px;
  height: 15px;
  padding: 0;
  border: none;
  background-color: var(--dvijok-tab-inactive);
  cursor: default;
  mask: url('/admin/icons/schedule/delete.svg') center / contain no-repeat;
  -webkit-mask: url('/admin/icons/schedule/delete.svg') center / contain no-repeat;

  &--active {
    background-color: var(--dvijok-blue-primary);
    cursor: pointer;

    &:hover {
      opacity: 0.8;
    }
  }

  &:disabled {
    opacity: 1;
  }

  &:focus-visible {
    outline: 2px solid var(--dvijok-blue-primary);
    outline-offset: 2px;
    border-radius: 2px;
  }
}

.schedule-settings__time-row {
  display: flex;
  align-items: center;
  gap: 9px;
  flex: 1;
  min-width: 0;
}

.schedule-settings__time-row > :deep(.base-input) {
  flex: 1;
  min-width: 0;
}

.schedule-settings__time-sep {
  flex-shrink: 0;
  width: 12px;
  height: 1px;
  background: var(--dvijok-text-secondary);
}

.schedule-settings__add {
  align-self: flex-start;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--dvijok-text-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 15px;
  text-align: left;

  &:hover {
    opacity: 0.8;
  }

  &:focus-visible {
    outline: 2px solid var(--dvijok-blue-primary);
    outline-offset: 2px;
    border-radius: 4px;
  }
}

.schedule-settings__weekdays :deep(.base-choice__option:nth-child(6)),
.schedule-settings__weekdays :deep(.base-choice__option:nth-child(7)) {
  color: var(--dvijok-weekend-muted);
  border-color: var(--dvijok-weekend-muted);
}

.schedule-settings__weekdays :deep(.base-choice__option--active:nth-child(6)),
.schedule-settings__weekdays :deep(.base-choice__option--active:nth-child(7)) {
  color: var(--dvijok-weekend-muted);
  background-color: var(--dvijok-choice-active);
  border-color: var(--dvijok-weekend-muted);
}

.schedule-settings__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: auto;
  flex-shrink: 0;
}

.schedule-settings__error {
  margin: 0;
  color: var(--dvijok-danger);
  font-size: 13px;
  line-height: 16px;
  text-align: center;
}
</style>
