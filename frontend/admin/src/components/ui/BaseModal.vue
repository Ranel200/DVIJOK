<template>
  <q-dialog
    v-model="modelValueProxy"
    class="base-modal"
    :class="{ 'base-modal--panel': isPanel }"
    transition-show="fade"
    transition-hide="fade"
    no-shake
    :persistent="persistent"
    @show="onShow"
    @hide="onHide"
  >
    <div
      class="base-modal__shell"
      :class="{
        'base-modal__shell--short': size === 'short',
        'base-modal__shell--panel': isPanel,
        'base-modal__shell--compact': compact
      }"
    >
      <div
        class="base-modal__card"
        :class="{
          'base-modal__card--fit': fit && !isPanel && size !== 'short',
          'base-modal__card--short': size === 'short',
          'base-modal__card--panel': isPanel,
          'base-modal__card--compact': compact
        }"
        :style="cardStyle"
        role="dialog"
        aria-modal="true"
      >
        <template v-if="isPanel">
          <div class="base-modal__panel-head">
            <div class="base-modal__panel-title-row">
              <h2
                v-if="title"
                class="base-modal__panel-title"
                :class="{ 'base-modal__panel-title--upper': titleUppercase }"
              >
                {{ title }}
              </h2>
              <div v-if="$slots['title-after']" class="base-modal__panel-title-after">
                <slot name="title-after" />
              </div>
            </div>
            <button
              v-if="!hideClose"
              type="button"
              class="base-modal__close base-modal__close--panel"
              aria-label="Закрыть"
              @click="close"
            >
              <CloseIcon :size="22" color="var(--dvijok-white)" />
            </button>
          </div>
          <div v-if="$slots.before" class="base-modal__panel-before">
            <slot name="before" />
          </div>
          <div class="base-modal__panel-divider" aria-hidden="true" />
          <div class="base-modal__content base-modal__content--panel">
            <slot />
          </div>
          <div v-if="$slots.actions" class="base-modal__panel-actions">
            <slot name="actions" />
          </div>
        </template>

        <template v-else>
          <button
            v-if="!hideClose"
            type="button"
            class="base-modal__close"
            aria-label="Закрыть"
            @click="close"
          >
            <CloseIcon :size="22" />
          </button>
          <div
            class="base-modal__content"
            :class="{
              'base-modal__content--fit': fit && size !== 'short',
              'base-modal__content--short': size === 'short'
            }"
          >
            <slot />
          </div>
        </template>
      </div>

      <div v-if="!isPanel && $slots.actions" class="base-modal__actions">
        <slot name="actions" />
      </div>
    </div>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'
import CloseIcon from '@/components/ui/CloseIcon.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  persistent: {
    type: Boolean,
    default: false
  },
  fit: {
    type: Boolean,
    default: false
  },
  hideClose: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'default',
    validator: value => ['default', 'short', 'panel'].includes(value)
  },
  padding: {
    type: String,
    default: ''
  },
  titleUppercase: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'show'])

const isPanel = computed(() => props.size === 'panel')

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

const cardStyle = computed(() => {
  if (isPanel.value) {
    return { padding: props.padding || '20px' }
  }
  const padding = props.padding || (props.size === 'short' ? '25px 15px' : '20px')
  return { padding }
})

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

.base-modal--panel .q-dialog__inner {
  padding: 40px;
  height: 100%;
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

.base-modal__shell--short {
  width: 480px;
  height: 100%;
}

.base-modal__shell--compact {
  width: auto;
  gap: 0;
}

.base-modal__shell--panel {
  width: 100%;
  height: 100%;
  max-height: 100%;
  gap: 0;
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

.base-modal__card--short {
  height: 100%;
  min-height: 0;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  overflow: visible;
}

.base-modal__card--panel {
  height: 100%;
  min-height: 0;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 20px;
  background: var(--dvijok-modal-panel);
  overflow: hidden;
}

.base-modal__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-shrink: 0;
  width: 100%;
}

.base-modal__panel-title-row {
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 0;
  flex: 1;
}

.base-modal__panel-title {
  margin: 0;
  color: var(--dvijok-white);
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
}

.base-modal__panel-title--upper {
  text-transform: uppercase;
}

.base-modal__panel-title-after {
  flex-shrink: 0;
}

.base-modal__panel-before {
  flex-shrink: 0;
  width: 100%;
}

.base-modal__panel-divider {
  flex-shrink: 0;
  width: 100%;
  height: 2px;
  background: var(--dvijok-blue-primary);
}

.base-modal__card--compact {
  height: auto;
  min-height: 0;
  border-radius: 10px;
  align-items: stretch;
  justify-content: flex-start;
  flex-direction: column;
  overflow: visible;
}

.base-modal__panel-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
  flex-shrink: 0;
  width: 100%;
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

.base-modal__close--panel {
  position: static;
  flex-shrink: 0;
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

.base-modal__content--short {
  flex: 1;
  min-height: 0;
  height: 100%;
  align-items: stretch;
  justify-content: flex-start;
  overflow: visible;
}

.base-modal__content--panel {
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
