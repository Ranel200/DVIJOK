<template>
  <AdminHeader
    :tabs="tabs"
    v-model:active-tab="activeTab"
    :action="action"
    @action-click="onAction"
  />
  <div class="crm"></div>
</template>

<script setup>
import { ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'

const tabs = [
  { label: 'Канбан', value: 'kanban' },
  { label: 'Список', value: 'list' }
]
const activeTab = ref('kanban')

const action = { label: '+ Новый заказ' }

function onAction() {
  // TODO: открыть форму нового заказа
}
</script>

<style scoped></style>
