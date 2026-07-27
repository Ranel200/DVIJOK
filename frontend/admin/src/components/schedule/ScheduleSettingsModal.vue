<template>
  <BaseModal v-model="open" size="short" hide-close persistent>
    <div class="schedule-settings">
      <h2 class="schedule-settings__title">Настройки графика</h2>

      <div class="schedule-settings__form">
        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Выберите тип</span>
          <BaseSelect
            v-model="draft.type"
            :options="typeOptions"
            placeholder="Выберите тип"
            block
          />
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Рабочее время</span>
          <div class="schedule-settings__time-row">
            <BaseInput v-model="draft.start" mask="##:##" block />
            <span class="schedule-settings__time-sep" aria-hidden="true" />
            <BaseInput v-model="draft.end" mask="##:##" block />
          </div>
          <div
            v-for="(breakItem, index) in draft.breaks"
            :key="index"
            class="schedule-settings__time-row"
          >
            <BaseInput v-model="breakItem.start" mask="##:##" block />
            <span class="schedule-settings__time-sep" aria-hidden="true" />
            <BaseInput v-model="breakItem.end" mask="##:##" block />
          </div>
          <button type="button" class="schedule-settings__add-break" @click="addBreak">
            + Добавить перерыв
          </button>
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Дни недели</span>
          <BaseChoice
            v-model="draft.workDays"
            class="schedule-settings__weekdays"
            :options="weekdayOptions"
            shape="rounded"
            multiple
            gap="10px"
          />
        </div>

        <div class="schedule-settings__field">
          <span class="schedule-settings__label">Применить к</span>
          <BaseSelect
            v-model="draft.employeeId"
            :options="employeeOptions"
            placeholder="Все сотрудники"
            block
          />
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

const typeOptions = [{ value: 'workdays', label: 'Рабочие дни' }]

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
    type: 'workdays',
    start: '09:00',
    end: '18:00',
    breaks: [],
    workDays: [1, 2, 3, 4, 5],
    employeeId: 'all'
  }
}

function resetDraft() {
  const next = createEmptyDraft()
  draft.type = next.type
  draft.start = next.start
  draft.end = next.end
  draft.breaks.splice(0, draft.breaks.length)
  draft.workDays.splice(0, draft.workDays.length, ...next.workDays)
  draft.employeeId = next.employeeId
}

function addBreak() {
  draft.breaks.push({ start: '', end: '' })
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

function validate() {
  const start = parseTimeMinutes(draft.start)
  const end = parseTimeMinutes(draft.end)
  if (start == null || end == null) {
    return 'Укажите корректное рабочее время (ЧЧ:ММ)'
  }
  if (start >= end) {
    return 'Время начала должно быть меньше времени окончания'
  }
  if (!draft.workDays.length) {
    return 'Выберите хотя бы один рабочий день'
  }
  for (const item of draft.breaks) {
    const breakStart = parseTimeMinutes(item.start)
    const breakEnd = parseTimeMinutes(item.end)
    if (breakStart == null || breakEnd == null) {
      return 'Укажите корректное время перерывов (ЧЧ:ММ)'
    }
    if (breakStart >= breakEnd) {
      return 'В перерыве время начала должно быть меньше окончания'
    }
    if (breakStart < start || breakEnd > end) {
      return 'Перерыв должен быть внутри рабочего времени'
    }
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
    await scheduleApi.saveSettings({
      type: draft.type,
      start: draft.start,
      end: draft.end,
      breaks: draft.breaks.map(item => ({ start: item.start, end: item.end })),
      workDays: [...draft.workDays],
      employeeId: draft.employeeId
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

.schedule-settings__time-row {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
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

.schedule-settings__add-break {
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
