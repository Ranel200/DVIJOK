<template>
  <q-page class="home">
    <ClientHeader :title="headerTitle" :subtitle="headerSubtitle" />

    <q-tab-panels v-model="tab" animated swipeable class="home__panels">
      <q-tab-panel name="book" class="home__panel">
        <BookPanel @go-to-car="tab = 'car'" />
      </q-tab-panel>

      <q-tab-panel name="car" class="home__panel">
        <CarPanel />
      </q-tab-panel>

      <q-tab-panel name="history" class="home__panel">
        <HistoryPanel />
      </q-tab-panel>
    </q-tab-panels>

    <HomeTabs v-model="tab" />
  </q-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth.js'
import BookPanel from '@/components/home/BookPanel.vue'
import CarPanel from '@/components/home/CarPanel.vue'
import HistoryPanel from '@/components/home/HistoryPanel.vue'
import HomeTabs from '@/components/home/HomeTabs.vue'
import ClientHeader from '@/components/layout/ClientHeader.vue'

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)
const tab = ref('car')

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) return 'Доброе утро,'
  if (hour >= 12 && hour < 18) return 'Добрый день,'
  return 'Добрый вечер,'
})

const userDisplayName = computed(() => {
  const name = user.value?.name?.trim()
  return name ? `${name}!` : 'Клиент!'
})

const headerTitle = computed(() => {
  if (tab.value === 'car') return userDisplayName.value
  if (tab.value === 'history') return 'История обслуживания'
  return 'Записаться'
})

const headerSubtitle = computed(() => {
  if (tab.value === 'car') return greeting.value
  return ''
})
</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  overflow: auto;
}

.home__panels {
  flex: 1;
  background: transparent;
}

.home__panel {
  padding: 0;
}
</style>
