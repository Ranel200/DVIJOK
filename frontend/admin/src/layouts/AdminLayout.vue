<template>
  <q-layout view="lHh Lpr lff">
    <AdminSidebar />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import AdminSidebar from '@/components/layout/AdminSidebar.vue'
</script>
