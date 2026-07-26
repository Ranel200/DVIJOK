<template>
  <q-dialog
    v-model="modelValueProxy"
    class="base-modal"
    transition-show="fade"
    transition-hide="fade"
    no-shake
    :persistent="persistent"
    @show="onShow"
    @hide="onHide"
  >
    <div class="base-modal__shell">
      <div
        class="base-modal__card"
        :class="{ 'base-modal__card--fit': fit }"
        :style="cardStyle"
        role="dialog"
        aria-modal="true"
      >
        <button
          v-if="!hideClose"
          type="button"
          class="base-modal__close"
          aria-label="Закрыть"
          @click="close"
        >
          <img src="/admin/icons/close-22.svg" alt="" width="22" height="22" />
        </button>
        <div class="base-modal__content" :class="{ 'base-modal__content--fit': fit }">
          <slot />
        </div>
      </div>

      <div v-if="$slots.actions" class="base-modal__actions">
        <slot name="actions" />
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
  },
  /** Высота по контенту вместо фиксированных 300px */
  fit: {
    type: Boolean,
    default: false
  },
  /** Скрыть крестик закрытия */
  hideClose: {
    type: Boolean,
    default: false
  },
  /** Внутренний отступ карточки */
  padding: {
    type: String,
    default: '20px'
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'show'])

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

const cardStyle = computed(() => ({
  padding: props.padding
}))

function close() {
  emit('update:modelValue', false)
}

function onShow() {
  emit('show')
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
  padding: 70px;
  box-sizing: border-box;
  --q-transition-duration: 40ms;
}

.base-modal .base-modal__card,
.base-modal .base-modal__content,
.base-modal .base-modal__shell {
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    width: 0;
    height: 0;
    display: none;
  }
}
</style>

<style scoped lang="scss">
.base-modal__shell {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 30px;
  width: 600px;
  max-width: 100%;
  max-height: 100%;
}

.base-modal__card {
  position: relative;
  width: 100%;
  height: 300px;
  flex-shrink: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--dvijok-white);
  border-radius: 15px;
  box-sizing: border-box;
  overflow: hidden;
}

.base-modal__card--fit {
  height: auto;
  max-height: 100%;
  min-height: 300px;
  overflow: hidden;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
}

.base-modal__close {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1;
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

.base-modal__content--fit {
  flex: 1;
  min-height: 0;
  height: auto;
  align-items: stretch;
  justify-content: flex-start;
  overflow: hidden;
}

.base-modal__actions {
  width: 100%;
  flex-shrink: 0;
}
</style>
