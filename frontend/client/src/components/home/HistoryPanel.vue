<template>
  <div class="history-panel">
    <template v-for="(section, index) in sections" :key="sectionKey(section, index)">
      <h2 v-if="section.label" class="history-panel__month">{{ section.label }}</h2>

      <div class="history-panel__list">
        <HistoryCard
          v-for="item in section.items"
          :key="item.id"
          :title="item.title"
          :status="item.status"
          :car-brand="item.carBrand"
          :car-plate="item.carPlate"
          :service-name="item.serviceName"
          :service-address="item.serviceAddress"
          :master="item.master"
          :datetime="item.datetime"
          :amount="item.amount"
          :order-number="item.orderNumber"
          :order-ready="item.orderReady"
          @open-order="onOpenOrder(item)"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { historyApi } from '@/api/index.js'
import HistoryCard from '@/components/home/HistoryCard.vue'

const items = ref([])

const sections = computed(() => {
  const activeItems = []
  const byMonth = new Map()

  for (const item of items.value) {
    if (item.status !== 'completed') {
      activeItems.push(item)
      continue
    }

    const label = item.monthLabel || ''
    if (!byMonth.has(label)) byMonth.set(label, [])
    byMonth.get(label).push(item)
  }

  const result = []
  if (activeItems.length) {
    result.push({ label: '', items: activeItems })
  }
  for (const [label, monthItems] of byMonth) {
    result.push({ label, items: monthItems })
  }
  return result
})

function sectionKey(section, index) {
  return section.label || `active-${index}`
}

async function onOpenOrder(item) {
  if (!item.orderReady) return

  const preview = window.open('about:blank', '_blank')
  if (preview) preview.opener = null

  try {
    const response = await historyApi.document(item.id)
    const documentBlob = await response.blob()
    const documentUrl = URL.createObjectURL(documentBlob)

    if (preview) {
      preview.location.replace(documentUrl)
    } else {
      const link = document.createElement('a')
      link.href = documentUrl
      link.target = '_blank'
      link.rel = 'noopener noreferrer'
      link.click()
    }

    window.setTimeout(() => URL.revokeObjectURL(documentUrl), 60_000)
  } catch (error) {
    preview?.close()
    throw error
  }
}

onMounted(async () => {
  const data = await historyApi.list()
  items.value = data.items || []
})
</script>

<style scoped lang="scss">
.history-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
}

.history-panel__month {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.history-panel__list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
