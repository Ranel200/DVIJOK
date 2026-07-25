<template>
  <AdminHeader :action="action" @action-click="onAction">
    <template #action-icon>
      <PrinterIcon />
    </template>
  </AdminHeader>
</template>

<script setup>
import AdminHeader from '@/components/layout/AdminHeader.vue'
import PrinterIcon from '@/components/ui/PrinterIcon.vue'

const action = { label: 'Напечатать QR-код' }

function onAction() {
  // TODO: печать QR-кода
}
</script>

<style scoped></style>
