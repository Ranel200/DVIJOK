<template>
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
  <div class="tasks"></div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import SummaryCards from '@/components/ui/SummaryCards.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import { tasksApi } from '@/api/index.js'
import { pluralize } from '@/utils/pluralize.js'

const action = { label: '+ Новая задача' }

const summary = ref(null)
const loading = ref(true)
const employees = ref([])

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

function onAction() {
  // TODO: открыть форму новой задачи
}

onMounted(async () => {
  try {
    const [summaryData, employeesData] = await Promise.all([
      tasksApi.summary(),
      tasksApi.employees()
    ])
    summary.value = summaryData
    employees.value = employeesData
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
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
