<template>
  <q-page class="home">
    <div class="home__toolbar">
      <q-btn flat dense color="primary" label="Выйти" @click="onLogout" />
    </div>

    <q-tab-panels v-model="tab" animated swipeable class="home__panels">
      <q-tab-panel name="book" class="home__panel">
        <BookPanel />
      </q-tab-panel>

      <q-tab-panel name="car" class="home__panel">
        <CarPanel />
      </q-tab-panel>

      <q-tab-panel name="history" class="home__panel">
        <HistoryPanel />
      </q-tab-panel>
    </q-tab-panels>

    <q-tabs
      v-model="tab"
      dense
      align="justify"
      class="home__tabs"
      active-color="primary"
      indicator-color="primary"
    >
      <q-tab
        v-for="item in clientTabs"
        :key="item.name"
        :name="item.name"
        :label="item.label"
        :aria-label="item.label"
      />
    </q-tabs>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { clientTabs } from '@/constants/navigation.js'
import BookPanel from '@/components/home/BookPanel.vue'
import CarPanel from '@/components/home/CarPanel.vue'
import HistoryPanel from '@/components/home/HistoryPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const tab = ref(clientTabs[0].name)

async function onLogout() {
  await authStore.logout()
  await router.push({ name: 'login' })
}
</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  overflow: auto;
}

.home__toolbar {
  display: flex;
  justify-content: flex-end;
  padding: 8px 12px 0;
}

.home__panels {
  flex: 1;
  background: transparent;
}

.home__panel {
  padding: 0;
}

.home__tabs {
  flex-shrink: 0;
}
</style>
