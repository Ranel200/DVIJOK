<template>
  <AdminHeader :action="action" @action-click="onAction" />
</template>

<script setup>
import AdminHeader from '@/components/layout/AdminHeader.vue'

const action = { label: '+ Добавить услугу' }

function onAction() {
  // TODO: открыть форму добавления услуги
}
</script>

<style scoped></style>
