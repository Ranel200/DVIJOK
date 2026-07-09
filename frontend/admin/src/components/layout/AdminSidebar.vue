<template>
  <q-drawer v-model="sidebarOpen" show-if-above bordered>
    <q-list>
      <q-item-label header>DVIJOK Admin</q-item-label>

      <q-item
        v-for="item in adminNavigation"
        :key="item.label"
        clickable
        :to="item.to"
        active-class="text-primary"
      >
        <q-item-section avatar>
          <q-icon :name="item.icon" />
        </q-item-section>

        <q-item-section>{{ item.label }}</q-item-section>
      </q-item>
    </q-list>
  </q-drawer>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app.js'
import { adminNavigation } from '@/constants/navigation.js'

const appStore = useAppStore()
const { sidebarOpen } = storeToRefs(appStore)
</script>
