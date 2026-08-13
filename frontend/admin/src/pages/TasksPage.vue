<template>
  <div class="tasks-page">
    <AdminHeader :action="action" @action-click="onAction">
      <template #below>
        <SummaryCards :cards="cards" :loading="loading" :count="5" />
        <div class="tasks-filters">
          <div
            v-if="authStore.isOwner"
            class="tasks-filters__field tasks-filters__field--employees"
          >
            <span class="tasks-filters__label">Отсортируйте по сотрудникам</span>
            <BaseSelect
              v-model="employee"
              :options="employeeOptions"
              placeholder="Все сотрудники"
              block
            />
          </div>
          <div class="tasks-filters__field tasks-filters__field--status">
            <span class="tasks-filters__label">Отсортируйте по статусу:</span>
            <BaseChoice
              v-model="status"
              :options="statusOptions"
              shape="pill"
              :multiple="true"
              :block="false"
              gap="15px"
            />
          </div>
        </div>
      </template>
    </AdminHeader>
    <AdminTable
      :columns="columns"
      :loading="loading"
      :empty="!filteredTasks.length"
      empty-text="Нет задач по выбранным фильтрам"
    >
      <template #head>
        <th class="admin-table__th admin-table__th--check"></th>
        <th class="admin-table__th tasks__th--task">Задача</th>
        <th class="admin-table__th tasks__th--employee">Сотрудник</th>
        <th class="admin-table__th tasks__th--deadline">Дедлайн</th>
        <th class="admin-table__th tasks__th--status">Статус</th>
        <th class="admin-table__th tasks__th--completion">Выполнение</th>
      </template>

      <tr v-for="task in filteredTasks" :key="task.id" class="admin-table__row">
        <td class="admin-table__cell admin-table__cell--check">
          <BaseCheckbox v-if="canManage" v-model="task._selected" />
        </td>
        <td class="admin-table__cell tasks__cell--task">
          <div class="admin-table__title">{{ task.title }}</div>
          <div class="admin-table__desc">{{ task.description }}</div>
        </td>
        <td class="admin-table__cell tasks__cell--employee">
          <span class="admin-table__text">{{ formatEmployee(task.employee) }}</span>
        </td>
        <td class="admin-table__cell tasks__cell--deadline">
          <span class="admin-table__text">{{ formatDeadline(task.deadline) }}</span>
        </td>
        <td class="admin-table__cell tasks__cell--status">
          <button
            type="button"
            :class="`tasks__pill tasks__pill--${task.status}`"
            title="Изменить статус"
            @click="cycleStatus(task)"
          >
            {{ statusLabel(task.status) }}
          </button>
        </td>
        <td class="admin-table__cell tasks__cell--completion">
          <span class="tasks__completion">
            <span class="tasks__completion-circle" aria-hidden="true" />
            <span class="tasks__completion-label">
              {{ task.status === 'done' ? 'Выполнена' : 'Не выполнено' }}
            </span>
          </span>
        </td>
      </tr>

      <template v-if="canManage" #footer>
        <BaseButton color="red" size="lg" :disable="!hasSelected" @click="onDeleteSelected">
          Удалить выбранные
        </BaseButton>
      </template>
    </AdminTable>

    <BaseModal v-model="createOpen" size="short" hide-close persistent>
      <div class="task-create">
        <h2 class="task-create__title">Добавить услугу</h2>
        <div class="task-create__form">
          <BaseField v-model="draft.title" label="Название задачи" block />
          <BaseField v-model="draft.description" label="Описание задачи" block />
          <div class="task-create__deadline">
            <BaseField
              v-model="draft.deadline"
              label="Срок выполнения"
              placeholder="дд.мм.гггг"
              mask="##.##.####"
              block
            />
          </div>
          <div class="task-create__field">
            <span class="task-create__label">Применить к</span>
            <BaseSelect
              v-model="draft.employeeId"
              :options="employeeOptions"
              placeholder="Все сотрудники"
              block
            />
          </div>
          <div class="task-create__field">
            <span class="task-create__label">Выберите статус</span>
            <BaseChoice
              v-model="draft.status"
              :options="statusOptions"
              shape="pill"
              :block="false"
              gap="15px"
            />
          </div>
        </div>
        <div class="task-create__actions">
          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-outlinedWhite"
            size="lg"
            @click="closeCreate"
          >
            Отмена
          </BaseButton>
          <BaseButton color="blue1" size="lg" :loading="saving" @click="saveCreate">
            Сохранить
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <SuccessModal v-model="savedOpen" :message="savedMessage" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import AdminTable from '@/components/ui/AdminTable.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import { tasksApi } from '@/api/index.js'
import { useAuthStore } from '@/stores/auth.js'
import { pluralize } from '@/utils/pluralize.js'
import { formatDeadlineUntil } from '@/utils/formatDateRu.js'

const authStore = useAuthStore()
const canManage = computed(() => authStore.canManageTasks)
const action = computed(() => (canManage.value ? { label: '+ Новая задача' } : null))

const columns = [
  { key: 'check', width: '63px' },
  { key: 'task', width: '25%' },
  { key: 'employee', width: '25%' },
  { key: 'deadline', width: '15%' },
  { key: 'status', width: '15%' },
  { key: 'completion', width: '160px' }
]

const summary = ref(null)
const loading = ref(true)
const employees = ref([])
const tasks = ref([])

const employee = ref('all')
const status = ref([])

const createOpen = ref(false)
const savedOpen = ref(false)
const saving = ref(false)
const savedTitle = ref('')
const savedMessage = computed(() => `Задача "${savedTitle.value}" добавлена!`)

const draft = reactive({
  title: '',
  description: '',
  deadline: '',
  employeeId: 'all',
  status: 'new'
})

const employeeOptions = computed(() => [
  { value: 'all', label: 'Все сотрудники' },
  ...employees.value.map(e => ({ value: e.id, label: `${e.name} — ${e.role}` }))
])

const statusOptions = [
  {
    label: 'Новая задача',
    value: 'new',
    color: 'var(--dvijok-blue-primary)',
    bg: 'var(--dvijok-choice-active)'
  },
  {
    label: 'Горящая задача',
    value: 'hot',
    color: '#F06D30',
    bg: '#F0E4D5'
  },
  {
    label: 'Сгоревшая задача',
    value: 'burned',
    color: 'var(--dvijok-danger-strong)',
    bg: '#F0D5D5'
  },
  {
    label: 'Выполнено',
    value: 'done',
    color: 'var(--dvijok-success)',
    bg: 'var(--dvijok-success-bg)'
  }
]

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const empOk =
      employee.value === 'all' || task.employee.id === employee.value || task.employee.id === 'all'
    const statusOk = !status.value.length || status.value.includes(task.status)
    return empOk && statusOk
  })
})

const hasSelected = computed(() => filteredTasks.value.some(task => task._selected))

watch(filteredTasks, visible => {
  const visibleIds = new Set(visible.map(task => task.id))
  for (const task of tasks.value) {
    if (task._selected && !visibleIds.has(task.id)) {
      task._selected = false
    }
  }
})

const cards = computed(() => {
  const s = summary.value
  const today = s?.today
  return [
    {
      title: 'На сегодня',
      special: true,
      serviceTitle: today ? String(today.count) : '',
      value: today
        ? `${today.overdue} ${pluralize(today.overdue, ['просрочен', 'просрочены', 'просрочено'])}`
        : ''
    },
    {
      title: 'Запланировано',
      value: s ? String(s.planned) : ''
    },
    {
      title: 'Выполнено за неделю',
      value: s ? String(s.donePerWeek) : ''
    }
  ]
})

function statusLabel(value) {
  const option = statusOptions.find(o => o.value === value)
  return option ? option.label : value
}

function formatDeadline(date) {
  return formatDeadlineUntil(date) || '—'
}

function formatEmployee(emp) {
  if (!emp || emp.id === 'all') return 'Все сотрудники'
  const parts = (emp.name || '').split(' ').filter(Boolean)
  const lastName = parts[0] || ''
  const firstInitial = parts[1] ? `${parts[1][0]}.` : ''
  return `${emp.role}: ${lastName}${firstInitial ? ' ' + firstInitial : ''}`.trim()
}

function deadlineToIso(value) {
  const match = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec((value || '').trim())
  if (!match) return ''
  const [, d, m, y] = match
  return `${y}-${m}-${d}`
}

function resolveEmployee(employeeId) {
  if (employeeId === 'all') {
    return { id: 'all', name: 'Все сотрудники', role: '' }
  }
  const found = employees.value.find(e => e.id === employeeId)
  return found
    ? { id: found.id, name: found.name, role: found.role }
    : { id: 'all', name: 'Все сотрудники', role: '' }
}

function resetDraft() {
  draft.title = ''
  draft.description = ''
  draft.deadline = ''
  draft.employeeId = 'all'
  draft.status = 'new'
}

function onAction() {
  if (!canManage.value) return
  resetDraft()
  createOpen.value = true
}

function closeCreate() {
  createOpen.value = false
}

async function saveCreate() {
  if (!canManage.value) return
  const title = draft.title.trim()
  if (!title || saving.value) return

  saving.value = true
  try {
    const created = await tasksApi.create({
      title,
      description: draft.description.trim(),
      deadline: deadlineToIso(draft.deadline),
      status: draft.status || 'new',
      employee: resolveEmployee(draft.employeeId)
    })
    tasks.value = [{ ...created, _selected: false }, ...tasks.value]
    savedTitle.value = created.title
    createOpen.value = false
    savedOpen.value = true
  } finally {
    saving.value = false
  }
}

async function onDeleteSelected() {
  if (!canManage.value) return
  if (!hasSelected.value) return
  const ids = tasks.value.filter(task => task._selected).map(task => task.id)
  await tasksApi.removeMany(ids)
  tasks.value = tasks.value.filter(task => !task._selected)
}

async function cycleStatus(task) {
  const currentIndex = statusOptions.findIndex(option => option.value === task.status)
  const next = statusOptions[(currentIndex + 1) % statusOptions.length]
  const updated = await tasksApi.updateStatus(task.id, next.value)
  Object.assign(task, updated, { _selected: task._selected })
}

onMounted(async () => {
  try {
    const [summaryData, employeesData, tasksData] = await Promise.all([
      tasksApi.summary(),
      tasksApi.employees(),
      tasksApi.list()
    ])
    summary.value = summaryData
    employees.value = employeesData
    tasks.value = tasksData.map(task => ({ ...task, _selected: false }))
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.tasks-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.tasks__th--task,
.tasks__cell--task,
.tasks__th--employee,
.tasks__cell--employee,
.tasks__th--deadline,
.tasks__cell--deadline,
.tasks__th--status,
.tasks__cell--status {
  padding-right: 40px;
}

.tasks__th--completion,
.tasks__cell--completion {
  padding-right: 19px;
  text-align: right;
}

.tasks__completion {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 7px 9px;
  border: 1px solid var(--dvijok-tab-inactive);
  border-radius: 50px;
  box-sizing: border-box;
}

.tasks__completion-circle {
  width: 20px;
  height: 20px;
  border: 2px solid var(--dvijok-tab-inactive);
  border-radius: 50%;
  box-sizing: border-box;
  flex-shrink: 0;
}

.tasks__completion-label {
  font-weight: 600;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-tab-inactive);
}

.tasks__pill {
  display: inline-block;
  padding: 6px 10px;
  border: none;
  border-radius: 50px;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
}

.tasks__pill--new {
  background-color: var(--dvijok-choice-active);
  color: var(--dvijok-blue-primary);
}

.tasks__pill--hot {
  background-color: #f0e4d5;
  color: #f06d30;
}

.tasks__pill--burned {
  background-color: #f0d5d5;
  color: var(--dvijok-danger-strong);
}

.tasks__pill--done {
  background-color: var(--dvijok-success-bg);
  color: var(--dvijok-success);
}

.tasks-filters {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
  margin-top: 16px;
}

.tasks-filters__field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tasks-filters__field--employees {
  width: 430px;
}

.tasks-filters__label {
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
}

.task-create {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  height: 100%;
}

.task-create__title {
  margin: 0;
  font-weight: 700;
  font-size: 24px;
  line-height: 36px;
  color: var(--dvijok-bg-dark);
}

.task-create__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.task-create__deadline {
  width: 200px;
}

.task-create__field {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.task-create__label {
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  line-height: 16px;
  text-align: left;
}

.task-create__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: auto;
}
</style>
