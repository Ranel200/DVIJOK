<template>
  <q-layout view="hHh lpR lFf">
    <q-header class="site-shell-header">
      <SiteHeader />
    </q-header>

    <q-page-container>
      <router-view />
      <SiteFooter />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import SiteFooter from '@/components/layout/SiteFooter.vue'
import SiteHeader from '@/components/layout/SiteHeader.vue'
</script>

<style scoped>
.site-shell-header {
  background: var(--dvijok-navy);
  box-shadow: 0 5px 20px 0 color-mix(in srgb, var(--dvijok-blue-bright) 40%, transparent);
}
</style>
