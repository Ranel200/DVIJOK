<template>
  <q-header elevated>
    <q-toolbar>
      <q-btn flat dense round icon="menu" aria-label="Меню" @click="appStore.toggleSidebar()" />

      <q-toolbar-title>{{ title }}</q-toolbar-title>

      <q-btn flat dense round icon="logout" aria-label="Выйти" @click="onLogout" />
    </q-toolbar>
  </q-header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app.js'
import { useAuthStore } from '@/stores/auth.js'

const appStore = useAppStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const title = computed(() => route.meta.title || 'DVIJOK Admin')

async function onLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>
