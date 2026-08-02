<template>
  <q-dialog
    v-model="modelValueProxy"
    class="base-modal"
    maximized
    no-shake
    :persistent="persistent"
    transition-show="fade"
    transition-hide="fade"
    @show="emit('show')"
    @hide="emit('close')"
  >
    <div class="base-modal__panel" role="dialog" aria-modal="true">
      <div class="base-modal__rounds" aria-hidden="true">
        <img class="base-modal__round base-modal__round--1" src="/client/round.svg" alt="" />
        <img class="base-modal__round base-modal__round--2" src="/client/round.svg" alt="" />
        <img class="base-modal__round base-modal__round--3" src="/client/round.svg" alt="" />
      </div>

      <div class="base-modal__content">
        <slot />
      </div>
    </div>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  persistent: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'show'])

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})
</script>

<style lang="scss">
.base-modal .q-dialog__inner {
  padding: 0;
  --q-transition-duration: 200ms;
}

.base-modal .q-dialog__backdrop {
  background: transparent;
  --q-transition-duration: 200ms;
}
</style>

<style scoped lang="scss">
.base-modal__panel {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 30px;
  overflow: hidden;
  box-sizing: border-box;
  background: var(--dvijok-gradient-brand);
}

.base-modal__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.base-modal__round {
  position: absolute;
  pointer-events: none;
  object-fit: contain;
  aspect-ratio: 1;
}

.base-modal__round--1 {
  width: 70%;
  top: 0;
  right: 0;
  transform: translate(15%, -25%);
}

.base-modal__round--2 {
  width: 45%;
  left: 0;
  bottom: 0;
  transform: translate(-50%, -56%);
}

.base-modal__round--3 {
  width: 90%;
  right: 0;
  bottom: 0;
  transform: translate(50%, 25%);
}

.base-modal__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
</style>
