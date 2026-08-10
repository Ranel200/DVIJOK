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
        <div class="status-overlay__round status-overlay__round--1">
          <span class="status-overlay__round-blur" />
          <img class="status-overlay__round-img" src="/client/round.svg" alt="" />
        </div>
        <div class="status-overlay__round status-overlay__round--2">
          <span class="status-overlay__round-blur" />
          <img class="status-overlay__round-img" src="/client/round.svg" alt="" />
        </div>
        <div class="status-overlay__round status-overlay__round--3">
          <span class="status-overlay__round-blur" />
          <img class="status-overlay__round-img" src="/client/round.svg" alt="" />
        </div>
      </div>

      <div class="status-overlay__content">
        <img
          v-if="mode === 'waiting'"
          class="status-overlay__logo"
          src="/client/icons/logo.png"
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
  background: var(--dvijok-gradient-brand);
}

.status-overlay__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.status-overlay__panel--waiting .status-overlay__rounds {
  z-index: 2;
}

.status-overlay__round {
  position: absolute;
  width: auto;
  height: auto;
}

.status-overlay__round--1 {
  width: 70vw;
  height: 70vw;
  top: 0;
  right: 0;
  transform: translate(10%, -25%);
}

.status-overlay__round--2 {
  width: 46vw;
  height: 46vw;
  bottom: 0;
  left: 0;
  transform: translate(-50%, -56%);
}

.status-overlay__round--3 {
  width: 96vw;
  height: 96vw;
  bottom: 0;
  right: 0;
  transform: translate(35%, 35%);
}

.status-overlay__round-blur {
  position: absolute;
  inset: 3%;
  border-radius: 50%;
  opacity: 0;
  background: transparent;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  mask-image: radial-gradient(circle closest-side, #000 100%, transparent 100%);
  -webkit-mask-image: radial-gradient(circle closest-side, #000 100%, transparent 100%);
}

.status-overlay__panel--waiting .status-overlay__round-blur {
  opacity: 1;
}

.status-overlay__round-img {
  position: relative;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
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
    transform: translate(10%, -25%) translateY(0);
  }

  to {
    transform: translate(10%, -25%) translateY(calc(100vh - 100%));
  }
}

@keyframes status-sway-2 {
  from {
    transform: translate(-50%, -56%) translateY(0);
  }

  to {
    transform: translate(-50%, -56%) translateY(calc(-100vh + 100%));
  }
}

@keyframes status-sway-3 {
  from {
    transform: translate(35%, 35%) translateY(0);
  }

  to {
    transform: translate(35%, 35%) translateY(calc(-100vh + 100%));
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
  width: 85vw;
  max-width: none;
  height: auto;
}

.status-overlay__loader {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.status-overlay__dot {
  --dot-size: 8.4px;
  position: absolute;
  top: 50%;
  left: 50%;
  width: var(--dot-size);
  height: var(--dot-size);
  margin: calc(var(--dot-size) / -2) 0 0 calc(var(--dot-size) / -2);
  border-radius: 50%;
  background: #c0d1ff;
  box-shadow: inset 0.5px 0.5px 0 rgba(255, 255, 255, 0.25);
  transform: rotate(calc(var(--i) * 30deg)) translateY(-36px);
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
  font-size: 80px;
  line-height: 97px;
  color: var(--dvijok-muted);
  text-align: center;
}

.status-overlay__text {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-muted);
  text-align: center;
  white-space: nowrap;
}
</style>
