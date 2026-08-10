<template>
  <router-view />
  <StatusOverlay />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import StatusOverlay from '@/components/system/StatusOverlay.vue'
import { useStatusOverlayStore } from '@/stores/statusOverlay.js'

const overlay = useStatusOverlayStore()
const WAITING_MS = 3000
let waitingTimer = null

onMounted(() => {
  overlay.showWaiting()
  waitingTimer = window.setTimeout(() => {
    if (overlay.mode === 'waiting') overlay.hide()
  }, WAITING_MS)
})

onUnmounted(() => {
  if (waitingTimer) window.clearTimeout(waitingTimer)
})
</script>
