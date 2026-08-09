<template>
  <q-page class="home">
    <ClientHeader :title="headerTitle" :subtitle="headerSubtitle" />

    <div class="home__body">
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

      <CookiesBanner
        v-if="tab === 'car' && cookiesVisible"
        class="home__cookies"
        @accept="acceptCookies"
      />
    </div>

    <HomeTabs v-model="tab" />
  </q-page>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth.js'
import { clientTabs } from '@/constants/navigation.js'
import BookPanel from '@/components/home/BookPanel.vue'
import CarPanel from '@/components/home/CarPanel.vue'
import CookiesBanner from '@/components/home/CookiesBanner.vue'
import HistoryPanel from '@/components/home/HistoryPanel.vue'
import HomeTabs from '@/components/home/HomeTabs.vue'
import ClientHeader from '@/components/layout/ClientHeader.vue'

const COOKIES_STORAGE_KEY = 'dvijok-cookies-accepted'

const route = useRoute()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const tabNames = new Set(clientTabs.map(item => item.name))
const initialTab = typeof route.query.tab === 'string' ? route.query.tab : ''
const tab = ref(tabNames.has(initialTab) ? initialTab : 'car')
const cookiesVisible = ref(localStorage.getItem(COOKIES_STORAGE_KEY) !== '1')

function acceptCookies() {
  localStorage.setItem(COOKIES_STORAGE_KEY, '1')
  cookiesVisible.value = false
}

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

.home__body {
  position: relative;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.home__panels {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: transparent;
}

.home__panel {
  padding: 0;
}

.home__cookies {
  position: absolute;
  left: 15px;
  right: 15px;
  bottom: 15px;
  z-index: 20;
}
</style>
