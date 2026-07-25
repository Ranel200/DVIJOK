<template>
  <q-dialog
    v-model="modelValueProxy"
    class="base-modal"
    transition-show="fade"
    transition-hide="fade"
    no-shake
    :persistent="persistent"
    @hide="onHide"
  >
    <div class="base-modal__card" role="dialog" aria-modal="true">
      <button type="button" class="base-modal__close" aria-label="Закрыть" @click="close">
        <img src="/admin/icons/close.svg" alt="" width="22" height="22" />
      </button>
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

const emit = defineEmits(['update:modelValue', 'close'])

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

function close() {
  emit('update:modelValue', false)
}

function onHide() {
  emit('close')
}
</script>

<style lang="scss">
.base-modal .q-dialog__backdrop {
  background: var(--dvijok-overlay);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  --q-transition-duration: 40ms;
}

.base-modal .q-dialog__inner {
  align-items: center;
  justify-content: center;
  --q-transition-duration: 40ms;
}
</style>

<style scoped lang="scss">
.base-modal__card {
  position: relative;
  width: 600px;
  height: 300px;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 32px);
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--dvijok-white);
  border-radius: 15px;
  box-sizing: border-box;
  overflow: hidden;
}

.base-modal__close {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.18s ease;

  &:hover {
    opacity: 0.7;
  }

  &:focus-visible {
    outline: 2px solid var(--dvijok-blue-primary);
    outline-offset: 2px;
    border-radius: 4px;
  }
}

.base-modal__content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
