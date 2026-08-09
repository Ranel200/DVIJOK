<template>
  <header class="client-header">
    <div class="client-header__rounds" aria-hidden="true">
      <img class="client-header__round client-header__round--1" src="/client/round.svg" alt="" />
      <img class="client-header__round client-header__round--2" src="/client/round.svg" alt="" />
    </div>

    <div class="client-header__body">
      <div class="client-header__text">
        <p class="client-header__subtitle">{{ subtitle || '\u00A0' }}</p>
        <h1 class="client-header__title">{{ title }}</h1>
      </div>

      <button
        v-if="showSettingsButton"
        type="button"
        class="client-header__settings"
        aria-label="Настройки"
        @click="goToSettings"
      >
        <img src="/client/icons/gear.svg" alt="" width="30" height="30" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

const showSettingsButton = computed(() => isAuthenticated.value && route.name !== 'settings')

function goToSettings() {
  router.push({ name: 'settings' })
}
</script>

<style scoped lang="scss">
.client-header {
  position: relative;
  flex-shrink: 0;
  padding: 20px 30px;
  overflow: hidden;
  background: var(--dvijok-gradient-brand);
}

.client-header__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.client-header__round {
  position: absolute;
  pointer-events: none;
  object-fit: contain;
}

.client-header__round--1 {
  width: 50%;
  aspect-ratio: 1;
  top: 0;
  right: 0;
  transform: translate(40%, -50%);
}

.client-header__round--2 {
  width: 30%;
  aspect-ratio: 1;
  bottom: 0;
  left: 0;
  transform: translate(-30%, 50%);
}

.client-header__body {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.client-header__text {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.client-header__subtitle {
  margin: 0;
  min-height: 16px;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-tab-inactive);
}

.client-header__title {
  margin: 0;
  font-weight: 600;
  font-size: 20px;
  line-height: 30px;
  color: var(--dvijok-white);
}

.client-header__settings {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  line-height: 0;
}
</style>
