<template>
  <AdminHeader :action="action" @action-click="onAction" />
</template>

<script setup>
import AdminHeader from '@/components/layout/AdminHeader.vue'

const action = { label: '+ Новая задача' }

function onAction() {
  // TODO: открыть форму новой задачи
}
</script>

<style scoped></style>
