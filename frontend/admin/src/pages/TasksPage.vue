<template>
  <div class="tasks-page">
    <AdminHeader :action="action" @action-click="onAction">
      <template #below>
        <SummaryCards :cards="cards" :loading="loading" :count="5" />
        <div class="tasks-filters">
          <div class="tasks-filters__field tasks-filters__field--employees">
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
    <div class="tasks">
      <div class="tasks__head">
        <table class="tasks__table tasks__table--head">
          <colgroup>
            <col class="tasks__col--check" />
            <col class="tasks__col--task" />
            <col class="tasks__col--employee" />
            <col class="tasks__col--status" />
          </colgroup>
          <thead>
            <tr>
              <th class="tasks__th tasks__th--check"></th>
              <th class="tasks__th tasks__th--task">Задача</th>
              <th class="tasks__th tasks__th--employee">Сотрудник</th>
              <th class="tasks__th tasks__th--status">Статус</th>
            </tr>
          </thead>
        </table>
      </div>
      <div class="tasks__list">
        <table class="tasks__table tasks__table--body">
          <colgroup>
            <col class="tasks__col--check" />
            <col class="tasks__col--task" />
            <col class="tasks__col--employee" />
            <col class="tasks__col--status" />
          </colgroup>
          <tbody>
            <tr
              v-for="task in filteredTasks"
              :key="task.id"
              class="tasks__row"
            >
              <td class="tasks__cell tasks__cell--check">
                <BaseCheckbox v-model="task._selected" />
              </td>
              <td class="tasks__cell tasks__cell--task">
                <div class="tasks__title">{{ task.title }}</div>
                <div class="tasks__desc">{{ task.description }}</div>
                <div class="tasks__deadline">
                  Срок выполнения: {{ formatDeadline(task.deadline) }}
                </div>
              </td>
              <td class="tasks__cell tasks__cell--employee">
                <span class="tasks__emp">{{ formatEmployee(task.employee) }}</span>
              </td>
              <td class="tasks__cell tasks__cell--status">
                <span :class="`tasks__pill tasks__pill--${task.status}`">
                  {{ statusLabel(task.status) }}
                </span>
              </td>
            </tr>
            <tr v-if="!filteredTasks.length">
              <td colspan="4" class="tasks__empty">Нет задач по выбранным фильтрам</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="tasks__footer">
        <BaseButton color="red" size="lg" :disable="!hasSelected" @click="onDeleteSelected">
          Удалить выбранные
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { tasksApi } from '@/api/index.js'
import { pluralize } from '@/utils/pluralize.js'

const action = { label: '+ Новая задача' }

const summary = ref(null)
const loading = ref(true)
const employees = ref([])
const tasks = ref([])

const employee = ref('all')
const status = ref([])

const employeeOptions = computed(() => [
  { value: 'all', label: 'Все сотрудники' },
  ...employees.value.map(e => ({ value: e.id, label: `${e.name} — ${e.role}` }))
])

const statusOptions = [
  {
    label: 'Новая задача',
    value: 'new',
    color: '#093095',
    bg: '#B3C8FF'
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
    color: '#B60000',
    bg: '#F0D5D5'
  },
  {
    label: 'Выполнено',
    value: 'done',
    color: '#157848',
    bg: '#D5F0E4'
  }
]

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const empOk = employee.value === 'all' || task.employee.id === employee.value
    const statusOk = !status.value.length || status.value.includes(task.status)
    return empOk && statusOk
  })
})

const hasSelected = computed(() => tasks.value.some(task => task._selected))

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
  if (!date) return '—'
  const [, m, d] = date.split('-')
  return `${d}.${m}`
}

function formatEmployee(emp) {
  const parts = (emp.name || '').split(' ').filter(Boolean)
  const lastName = parts[0] || ''
  const firstInitial = parts[1] ? `${parts[1][0]}.` : ''
  return `${emp.role}: ${lastName}${firstInitial ? ' ' + firstInitial : ''}`.trim()
}

function onAction() {
  // TODO: открыть форму новой задачи
}

function onDeleteSelected() {
  if (!hasSelected.value) return
  tasks.value = tasks.value.filter(task => !task._selected)
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

.tasks {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 20px 20px;
}

.tasks__list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background-color: var(--dvijok-white);
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tasks__list::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.tasks__head {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.tasks__table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

.tasks__col--check {
  width: 63px;
}

.tasks__col--task {
  width: 45%;
}

.tasks__col--employee {
  width: auto;
}

.tasks__col--status {
  width: 139px;
}

.tasks__row {
  border-bottom: 1px solid var(--dvijok-text-secondary);
}

.tasks__row:last-child {
  border-bottom: none;
}

.tasks__th,
.tasks__cell {
  padding: 9px 0;
  text-align: left;
  vertical-align: middle;
  box-sizing: border-box;
}

.tasks__th--task,
.tasks__cell--task,
.tasks__th--employee,
.tasks__cell--employee {
  padding-right: 40px;
}

.tasks__th--check,
.tasks__cell--check {
  padding-left: 19px;
}

.tasks__th--status,
.tasks__cell--status {
  padding-right: 19px;
  text-align: right;
}

.tasks__th {
  font-weight: 700;
  font-size: 12px;
  line-height: 19px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.tasks__title {
  font-weight: 700;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tasks__desc {
  margin-top: 4px;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tasks__deadline {
  margin-top: 12px;
  font-weight: 600;
  font-size: 10px;
  line-height: 12px;
  color: var(--dvijok-text-secondary);
}

.tasks__emp {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-link-hover);
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
  background-color: #b3c8ff;
  color: #093095;
}

.tasks__pill--hot {
  background-color: #f0e4d5;
  color: #f06d30;
}

.tasks__pill--burned {
  background-color: #f0d5d5;
  color: #b60000;
}

.tasks__pill--done {
  background-color: #d5f0e4;
  color: #157848;
}

.tasks__empty {
  padding: 20px 19px;
  text-align: center;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.tasks__footer {
  margin-top: 40px;
  display: flex;
  justify-content: flex-start;
  flex-shrink: 0;
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
</style>
