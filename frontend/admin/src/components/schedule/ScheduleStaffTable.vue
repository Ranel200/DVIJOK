<template>
  <div class="schedule-staff" :style="columnVars">
    <div ref="panelRef" class="schedule-staff__panel">
      <div class="schedule-staff__table-wrap">
        <div
          v-if="todayBgStyle"
          class="schedule-staff__today-bg"
          :style="todayBgStyle"
          aria-hidden="true"
        />
        <div
          class="schedule-staff__sticky-mask schedule-staff__sticky-mask--top"
          aria-hidden="true"
        />
        <table class="schedule-staff__table">
          <colgroup>
            <col class="schedule-staff__col schedule-staff__col--employees" />
            <col class="schedule-staff__col schedule-staff__col--dots" />
            <col class="schedule-staff__col schedule-staff__col--total" />
            <col class="schedule-staff__col schedule-staff__col--gap" />
            <col
              v-for="day in monthDays"
              :key="`col-${day.day}`"
              class="schedule-staff__col schedule-staff__col--day"
            />
          </colgroup>
          <thead>
            <tr>
              <th class="schedule-staff__th schedule-staff__th--employees">
                Сотрудники ({{ employees.length }})
              </th>
              <th class="schedule-staff__th schedule-staff__th--dots"></th>
              <th class="schedule-staff__th schedule-staff__th--total">
                <div class="schedule-staff__total-head">
                  <span class="schedule-staff__total-title">Всего</span>
                  <span class="schedule-staff__total-sub">За месяц</span>
                </div>
              </th>
              <th class="schedule-staff__th schedule-staff__th--gap"></th>
              <th
                v-for="day in monthDays"
                :key="`th-${day.day}`"
                class="schedule-staff__th schedule-staff__th--day"
                :class="{ 'schedule-staff__th--weekend': day.isWeekend }"
              >
                <div class="schedule-staff__day-head">
                  <span class="schedule-staff__day-num">{{ day.day }}</span>
                  <span class="schedule-staff__day-week">{{ day.weekdayLabel }}</span>
                  <span class="schedule-staff__day-people">
                    <span>{{ day.peopleCount }}</span>
                    <img src="/admin/icons/schedule/group.svg" alt="" />
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employees" :key="employee.id" class="schedule-staff__row">
              <td class="schedule-staff__td schedule-staff__td--employees">
                <div class="schedule-staff__employee">
                  <div
                    class="schedule-staff__avatar"
                    :style="{ backgroundColor: employee.avatarBg }"
                  >
                    {{ getInitials(employee.name) }}
                  </div>
                  <div class="schedule-staff__employee-text">
                    <span class="schedule-staff__employee-name">{{
                      formatStaffName(employee.name)
                    }}</span>
                    <span class="schedule-staff__employee-role">{{ employee.role }}</span>
                  </div>
                </div>
              </td>
              <td class="schedule-staff__td schedule-staff__td--dots">
                <DotsMenu
                  :open="menuEmployeeId === employee.id"
                  :items="menuItems"
                  @update:open="open => onMenuOpen(employee.id, open)"
                  @select="key => onMenuSelect(key, employee)"
                />
              </td>
              <td class="schedule-staff__td schedule-staff__td--total">
                <div class="schedule-staff__month-total">
                  <span class="schedule-staff__month-days">{{ employee.totalDays }} д.</span>
                  <span class="schedule-staff__month-hours">{{ employee.totalHours }} ч.</span>
                </div>
              </td>
              <td class="schedule-staff__td schedule-staff__td--gap"></td>
              <td
                v-for="day in employee.days"
                :key="`${employee.id}-${day.day}`"
                class="schedule-staff__td schedule-staff__td--day"
              >
                <div
                  class="schedule-staff__shift"
                  :class="
                    day.active ? 'schedule-staff__shift--active' : 'schedule-staff__shift--inactive'
                  "
                >
                  <template v-if="day.active">
                    <span>{{ day.start }}</span>
                    <span>{{ day.end }}</span>
                  </template>
                  <span v-else class="schedule-staff__shift-dash" />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div
          class="schedule-staff__sticky-mask schedule-staff__sticky-mask--bottom"
          aria-hidden="true"
        />
      </div>
    </div>

    <div class="schedule-staff__footer">
      <BaseButton color="blue1" size="lg" @click="onAddEmployee">+ Добавить сотрудника</BaseButton>
    </div>

    <ScheduleStaffModal
      v-model="formOpen"
      :mode="formMode"
      :employee="editingEmployee"
      :saving="formSaving"
      @save="onSaveEmployee"
      @edit="onEditFromView"
      @delete="onDeleteFromView"
    />

    <BaseModal v-model="deleteConfirmOpen">
      <div class="schedule-staff__confirm">
        <h2 class="schedule-staff__confirm-title">
          Удалить сотрудника «{{ pendingDeleteName }}»?
        </h2>
        <div class="schedule-staff__confirm-actions">
          <BaseButton color="green" size="lg" @click="closeDeleteConfirm">Отмена</BaseButton>
          <BaseButton color="red" size="lg" :loading="deleting" @click="confirmDelete">
            Удалить
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <SuccessModal v-model="resultOpen" :message="resultMessage" />
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ScheduleStaffModal from '@/components/schedule/ScheduleStaffModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import DotsMenu from '@/components/ui/DotsMenu.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import { scheduleApi } from '@/api/index.js'
import { useScheduleFilterStore } from '@/stores/scheduleFilter.js'
import { getInitials, formatStaffName } from '@/utils/name.js'

const props = defineProps({
  visible: {
    type: Boolean,
    default: true
  }
})

const WEEKDAY_LABELS = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

const COL = {
  employees: 250,
  dots: 24,
  total: 100,
  gap: 10,
  day: 74
}
const COLS_BEFORE_DAYS = COL.employees + COL.dots + COL.total + COL.gap

const columnVars = {
  '--schedule-col-employees': `${COL.employees}px`,
  '--schedule-col-dots': `${COL.dots}px`,
  '--schedule-col-total': `${COL.total}px`,
  '--schedule-col-gap': `${COL.gap}px`,
  '--schedule-col-day': `${COL.day}px`,
  '--schedule-sticky-dots': `${COL.employees}px`,
  '--schedule-sticky-total': `${COL.employees + COL.dots}px`,
  '--schedule-sticky-gap': `${COL.employees + COL.dots + COL.total}px`,
  '--schedule-sticky-width': `${COLS_BEFORE_DAYS}px`
}

const menuItems = [
  { key: 'open', label: 'Открыть', icon: '/admin/icons/schedule/open.svg' },
  { key: 'edit', label: 'Редактировать', icon: '/admin/icons/services/edit.svg' },
  {
    key: 'delete',
    label: 'Удалить',
    icon: '/admin/icons/services/delete.svg',
    danger: true
  }
]

const scheduleFilter = useScheduleFilterStore()
const { monthDate } = storeToRefs(scheduleFilter)

const panelRef = ref(null)
const employees = ref([])
const menuEmployeeId = ref(null)
const deleteConfirmOpen = ref(false)
const pendingDeleteId = ref(null)
const pendingDeleteName = ref('')
const deleting = ref(false)
const formOpen = ref(false)
const formMode = ref('create')
const formSaving = ref(false)
const editingEmployee = ref(null)
const resultOpen = ref(false)
const resultMessage = ref('')

const today = new Date()

const monthMeta = computed(() => ({
  year: monthDate.value.getFullYear(),
  month: monthDate.value.getMonth()
}))

const isCurrentMonth = computed(
  () => monthMeta.value.year === today.getFullYear() && monthMeta.value.month === today.getMonth()
)

const todayBgStyle = computed(() => {
  if (!isCurrentMonth.value) return null
  const dayIndex = today.getDate() - 1
  return {
    left: `${COLS_BEFORE_DAYS + dayIndex * COL.day}px`,
    width: `${COL.day}px`
  }
})

const monthDays = computed(() => {
  const { year, month } = monthMeta.value
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const result = []

  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day)
    const weekday = date.getDay()
    const peopleCount = employees.value.reduce((count, employee) => {
      const shift = employee.days?.[day - 1]
      return shift?.active ? count + 1 : count
    }, 0)

    result.push({
      day,
      weekday,
      weekdayLabel: WEEKDAY_LABELS[weekday],
      isWeekend: weekday === 0 || weekday === 6,
      peopleCount
    })
  }

  return result
})

function onMenuOpen(employeeId, open) {
  menuEmployeeId.value = open ? employeeId : null
}

function onMenuSelect(key, employee) {
  if (key === 'open') {
    openEmployeeForm(employee.id, 'view')
    return
  }
  if (key === 'edit') {
    openEmployeeForm(employee.id, 'edit')
    return
  }
  if (key === 'delete') {
    pendingDeleteId.value = employee.id
    pendingDeleteName.value = formatStaffName(employee.name)
    deleteConfirmOpen.value = true
  }
}

function closeDeleteConfirm() {
  deleteConfirmOpen.value = false
  pendingDeleteId.value = null
  pendingDeleteName.value = ''
}

async function confirmDelete() {
  const id = pendingDeleteId.value
  const name = pendingDeleteName.value
  if (id == null) return
  deleting.value = true
  try {
    await scheduleApi.removeEmployee(id)
    employees.value = employees.value.filter(item => item.id !== id)
    closeDeleteConfirm()
    resultMessage.value = `Сотрудник ${name} удален!`
    resultOpen.value = true
  } finally {
    deleting.value = false
  }
}

function onAddEmployee() {
  editingEmployee.value = null
  formMode.value = 'create'
  formOpen.value = true
}

async function openEmployeeForm(id, mode) {
  const detail = await scheduleApi.getEmployee(id)
  editingEmployee.value = detail
  formMode.value = mode
  formOpen.value = true
}

function onEditFromView() {
  formMode.value = 'edit'
}

function onDeleteFromView() {
  if (!editingEmployee.value?.id) return
  pendingDeleteId.value = editingEmployee.value.id
  pendingDeleteName.value = formatStaffName(editingEmployee.value.name)
  formOpen.value = false
  deleteConfirmOpen.value = true
}

async function onSaveEmployee(draft) {
  formSaving.value = true
  try {
    const isEdit = formMode.value === 'edit'
    if (isEdit) {
      await scheduleApi.updateEmployee(editingEmployee.value.id, draft)
    } else {
      await scheduleApi.createEmployee(draft)
    }
    await loadEmployees()
    formOpen.value = false
    editingEmployee.value = null
    formMode.value = 'create'
    const shortName = formatStaffName(draft.name)
    resultMessage.value = isEdit
      ? `Сотрудник ${shortName} сохранен!`
      : `Сотрудник ${shortName} добавлен!`
    resultOpen.value = true
  } finally {
    formSaving.value = false
  }
}

async function scrollToToday() {
  if (!isCurrentMonth.value) return
  await nextTick()
  const panel = panelRef.value
  if (!panel) return

  const dayIndex = today.getDate() - 1
  const daysViewport = Math.max(0, panel.clientWidth - COLS_BEFORE_DAYS)
  panel.scrollLeft = Math.max(0, dayIndex * COL.day - (daysViewport - COL.day) / 2)
}

async function loadEmployees() {
  const { year, month } = monthMeta.value
  const data = await scheduleApi.employees({ year, month })
  employees.value = data
  menuEmployeeId.value = null
  if (props.visible) await scrollToToday()
}

watch(monthMeta, loadEmployees, { immediate: true })

watch(
  () => props.visible,
  async value => {
    if (value) await scrollToToday()
  }
)

defineExpose({ reload: loadEmployees })
</script>

<style scoped lang="scss">
.schedule-staff {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 20px 20px;
}

.schedule-staff__panel {
  flex: 1;
  min-height: 0;
  overflow: auto;
  box-sizing: border-box;
  background-color: var(--dvijok-white);
  border-radius: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.schedule-staff__panel::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.schedule-staff__table-wrap {
  position: relative;
  width: max-content;
  min-width: 100%;
  padding: 10px 10px 10px 0;
  box-sizing: border-box;
}

.schedule-staff__today-bg {
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: 0;
  box-sizing: border-box;
  background-color: var(--dvijok-choice-active);
  border: 1px solid var(--dvijok-today);
  border-radius: 8px;
  pointer-events: none;
}

.schedule-staff__sticky-mask {
  position: sticky;
  left: 0;
  z-index: 4;
  width: var(--schedule-sticky-width);
  height: 10px;
  background-color: var(--dvijok-white);
  pointer-events: none;
}

.schedule-staff__sticky-mask--top {
  top: 0;
  margin-top: -10px;
  margin-bottom: -10px;
}

.schedule-staff__sticky-mask--bottom {
  bottom: 0;
  margin-bottom: -10px;
}

.schedule-staff__table {
  position: relative;
  z-index: 1;
  width: max-content;
  min-width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  border-spacing: 0;
}

.schedule-staff__col--employees {
  width: var(--schedule-col-employees);
}

.schedule-staff__col--dots {
  width: var(--schedule-col-dots);
}

.schedule-staff__col--total {
  width: var(--schedule-col-total);
}

.schedule-staff__col--gap {
  width: var(--schedule-col-gap);
}

.schedule-staff__col--day {
  width: var(--schedule-col-day);
}

.schedule-staff__th,
.schedule-staff__td {
  vertical-align: middle;
  box-sizing: border-box;
  background-color: var(--dvijok-white);
}

.schedule-staff__th--employees,
.schedule-staff__td--employees {
  position: sticky;
  left: 0;
  z-index: 3;
}

.schedule-staff__th--dots,
.schedule-staff__td--dots {
  position: sticky;
  left: var(--schedule-sticky-dots);
  z-index: 3;
}

.schedule-staff__th--total,
.schedule-staff__td--total {
  position: sticky;
  left: var(--schedule-sticky-total);
  z-index: 3;
}

.schedule-staff__th--gap,
.schedule-staff__td--gap {
  position: sticky;
  left: var(--schedule-sticky-gap);
  z-index: 3;
}

.schedule-staff__th--employees {
  padding: 0 10px 30px 20px;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-link-hover);
  text-align: left;
}

.schedule-staff__th--dots {
  padding: 0 0 30px;
}

.schedule-staff__th--total {
  padding: 0 10px 30px;
  text-align: center;
}

.schedule-staff__th--gap {
  padding: 0 0 30px;
}

.schedule-staff__th--day {
  padding: 0 5px 30px;
  text-align: center;
  background-color: transparent;
}

.schedule-staff__total-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.schedule-staff__total-title {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link-hover);
  text-align: center;
}

.schedule-staff__total-sub {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
  text-align: center;
}

.schedule-staff__td--gap {
  padding: 0;
}

.schedule-staff__day-head {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  margin-top: 16px;
}

.schedule-staff__day-num {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
  text-align: center;
}

.schedule-staff__day-week {
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
  text-align: center;
}

.schedule-staff__th--weekend .schedule-staff__day-num {
  color: var(--dvijok-danger-strong);
}

.schedule-staff__th--weekend .schedule-staff__day-week {
  color: var(--dvijok-weekend-muted);
}

.schedule-staff__day-people {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}

.schedule-staff__day-people img {
  display: block;
  width: 12px;
  height: 6px;
}

.schedule-staff__td--employees {
  padding: 8px 10px 8px 20px;
}

.schedule-staff__row + .schedule-staff__row .schedule-staff__td--employees {
  padding-top: 23px;
}

.schedule-staff__row + .schedule-staff__row .schedule-staff__td--dots,
.schedule-staff__row + .schedule-staff__row .schedule-staff__td--total,
.schedule-staff__row + .schedule-staff__row .schedule-staff__td--gap {
  padding-top: 15px;
}

.schedule-staff__row + .schedule-staff__row .schedule-staff__td--day {
  padding-top: 15px;
}

.schedule-staff__employee {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.schedule-staff__avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 18px;
  color: var(--dvijok-white);
  font-size: 12px;
  font-weight: 600;
  line-height: 15px;
}

.schedule-staff__employee-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.schedule-staff__employee-name {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link-hover);
}

.schedule-staff__employee-role {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.schedule-staff__td--dots {
  padding: 0;
  text-align: center;
}

.schedule-staff__td--total {
  padding: 0 10px;
  text-align: center;
}

.schedule-staff__month-total {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.schedule-staff__month-days {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  text-align: center;
  color: var(--dvijok-link-hover);
}

.schedule-staff__month-hours {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  text-align: center;
  color: var(--dvijok-text-secondary);
}

.schedule-staff__td--day {
  padding: 0 5px;
  background-color: transparent;
}

.schedule-staff__shift {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 0 10px;
  box-sizing: border-box;
  border-radius: 8px;
  border: 1px solid;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  text-align: center;
}

.schedule-staff__shift--active {
  background-color: var(--dvijok-workday-bg);
  border-color: var(--dvijok-workday);
  color: var(--dvijok-workday);
}

.schedule-staff__shift--inactive {
  background-color: var(--dvijok-white);
  border-color: var(--dvijok-text-secondary);
}

.schedule-staff__shift-dash {
  display: block;
  width: 15px;
  height: 1px;
  background-color: var(--dvijok-text-secondary);
}

.schedule-staff__footer {
  margin-top: 30px;
  display: flex;
  justify-content: flex-start;
  flex-shrink: 0;
}

.schedule-staff__confirm {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.schedule-staff__confirm-title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}

.schedule-staff__confirm-actions {
  display: flex;
  gap: 16px;
}
</style>
