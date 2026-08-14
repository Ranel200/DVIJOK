<template>
  <q-dialog
    :model-value="isOpen"
    class="status-overlay"
    maximized
    persistent
    no-shake
    transition-show="fade"
    transition-hide="fade"
  >
    <div
      class="status-overlay__panel"
      :class="modeClass"
      role="dialog"
      aria-modal="true"
      :aria-label="ariaLabel"
    >
      <div class="status-overlay__rounds" aria-hidden="true">
        <img class="status-overlay__round status-overlay__round--1" src="/admin/round.svg" alt="" />
        <img class="status-overlay__round status-overlay__round--2" src="/admin/round.svg" alt="" />
        <img class="status-overlay__round status-overlay__round--3" src="/admin/round.svg" alt="" />
      </div>

      <div class="status-overlay__content">
        <img
          v-if="mode === 'waiting'"
          class="status-overlay__logo"
          src="/admin/icons/auth/logo-auth.png"
          alt="DVIJOK"
        />

        <template v-else-if="mode === 'loading'">
          <div class="status-overlay__loader" aria-hidden="true">
            <span
              v-for="dot in 12"
              :key="dot"
              class="status-overlay__dot"
              :style="{ '--i': dot - 1 }"
            />
          </div>
          <p class="status-overlay__text">Пожалуйста, подождите</p>
        </template>

        <template v-else-if="mode === 'error'">
          <p class="status-overlay__face" aria-hidden="true">:(</p>
          <p class="status-overlay__text">Кажется, возникла ошибка</p>
        </template>
      </div>
    </div>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useStatusOverlayStore } from '@/stores/statusOverlay.js'

const store = useStatusOverlayStore()
const { mode, isOpen } = storeToRefs(store)

const modeClass = computed(() => (mode.value ? `status-overlay__panel--${mode.value}` : null))

const ariaLabel = computed(() => {
  if (mode.value === 'waiting') return 'Ожидание'
  if (mode.value === 'loading') return 'Загрузка'
  if (mode.value === 'error') return 'Ошибка'
  return 'Системный экран'
})
</script>

<style lang="scss">
.status-overlay .q-dialog__inner {
  padding: 0;
  --q-transition-duration: 200ms;
}

.status-overlay .q-dialog__backdrop {
  background: transparent;
  --q-transition-duration: 200ms;
}
</style>

<style scoped lang="scss">
.status-overlay__panel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--dvijok-bg-dark);
}

.status-overlay__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.status-overlay__round {
  position: absolute;
  display: block;
  pointer-events: none;
  object-fit: contain;
  width: auto;
  height: auto;
}

.status-overlay__round--1 {
  width: 28.8vw;
  height: 28.8vw;
  top: 0;
  left: 0;
  transform: translate(-40%, -40%);
}

.status-overlay__round--2 {
  width: 42.6vw;
  height: 42.6vw;
  top: -16%;
  right: -8%;
}

.status-overlay__round--3 {
  width: 26.6vw;
  height: 26.6vw;
  bottom: 0;
  left: 20vw;
  transform: translate(-50%, 50%);
}

.status-overlay__panel--waiting .status-overlay__round--1 {
  animation: status-sway-1 1.9s ease-in-out infinite alternate;
}

.status-overlay__panel--waiting .status-overlay__round--2 {
  animation: status-sway-2 1.9s ease-in-out infinite alternate;
}

.status-overlay__panel--waiting .status-overlay__round--3 {
  animation: status-sway-3 1.9s ease-in-out infinite alternate;
}

@keyframes status-sway-1 {
  from {
    transform: translate(-40%, -40%) translateX(0);
  }

  to {
    transform: translate(-40%, -40%) translateX(calc(100vw - 100%));
  }
}

@keyframes status-sway-2 {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(calc(-100vw + 100%));
  }
}

@keyframes status-sway-3 {
  from {
    transform: translate(-50%, 50%) translateX(0);
  }

  to {
    transform: translate(-50%, 50%) translateX(calc(100vw - 100%));
  }
}

.status-overlay__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
  max-width: 100%;
}

.status-overlay__logo {
  display: block;
  width: 55vw;
  max-width: none;
  height: auto;
}

.status-overlay__loader {
  position: relative;
  width: 148px;
  height: 148px;
  flex-shrink: 0;
}

.status-overlay__dot {
  --dot-size: 15.5px;
  position: absolute;
  top: 50%;
  left: 50%;
  width: var(--dot-size);
  height: var(--dot-size);
  margin: calc(var(--dot-size) / -2) 0 0 calc(var(--dot-size) / -2);
  border-radius: 50%;
  background: #c0d1ff;
  box-shadow: inset 0.5px 0.5px 0 rgba(255, 255, 255, 0.25);
  transform: rotate(calc(var(--i) * 30deg)) translateY(-66px);
  animation: status-dot 1.2s linear infinite;
  animation-delay: calc(var(--i) * -0.1s);
}

@keyframes status-dot {
  0%,
  39%,
  100% {
    opacity: 0.12;
  }

  40% {
    opacity: 1;
  }
}

.status-overlay__face {
  margin: 0;
  font-weight: 600;
  font-size: 100px;
  line-height: 1.21;
  color: var(--dvijok-muted);
  text-align: center;
}

.status-overlay__text {
  margin: 0;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-muted);
  text-align: center;
  white-space: nowrap;
}
</style>
