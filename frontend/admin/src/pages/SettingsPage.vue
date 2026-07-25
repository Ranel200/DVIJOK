<template>
  <AdminHeader :tabs="tabs" v-model:active-tab="activeTab" :gap="0" />
  <div class="settings"></div>
</template>

<script setup>
import { ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'

const tabs = [
  { label: 'Автосервис', value: 'service' },
  { label: 'Безопасность', value: 'security' }
]
const activeTab = ref('service')
</script>

<style scoped></style>
