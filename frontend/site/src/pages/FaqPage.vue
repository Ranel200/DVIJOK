<template>
  <q-page padding>
    <h1>{{ title }}</h1>
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || 'DVIJOK')
</script>

<style scoped></style>
