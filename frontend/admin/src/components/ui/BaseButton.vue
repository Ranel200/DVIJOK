<template>
  <q-btn
    :class="[
      'base-btn',
      `base-btn--${color}`,
      `base-btn--${size}`,
      { 'base-btn--block': block, 'base-btn--text': text }
    ]"
    :style="stateVars"
    unelevated
    no-caps
    :type="type"
    :loading="loading"
    :disable="disable"
    @click="$emit('click', $event)"
  >
    <q-icon v-if="icon" :name="icon" size="1.2em" class="base-btn__icon" />
    <slot />
  </q-btn>
</template>

<script setup>
import { computed } from 'vue'
import { BUTTON_SCHEMES, DEFAULT_BUTTON_SCHEME } from './buttonSchemes.js'

const VARIANT_STYLE = {
  solid: { bg: 'var(--btn-solid)', color: '#fff', border: 'transparent' },
  light: { bg: 'var(--btn-light)', color: '#fff', border: 'transparent' },
  accent: {
    bg: 'var(--btn-accent-fill)',
    color: '#fff',
    border: 'transparent'
  },
  outlined: {
    bg: 'transparent',
    color: 'var(--btn-accent)',
    border: 'var(--btn-accent)'
  }
}

const props = defineProps({
  color: {
    type: String,
    default: 'blue1',
    validator: value => ['blue1', 'blue2', 'green', 'red'].includes(value)
  },
  scheme: {
    type: String,
    default: DEFAULT_BUTTON_SCHEME,
    validator: value => value in BUTTON_SCHEMES
  },
  size: {
    type: String,
    default: 'lg',
    validator: value => ['sm', 'lg'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'button'
  },
  loading: {
    type: Boolean,
    default: false
  },
  disable: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  },
  text: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const stateVars = computed(() => {
  const scheme = BUTTON_SCHEMES[props.scheme]
  const build = key => {
    const v = VARIANT_STYLE[scheme[key]]
    return {
      [`--btn-state-${key}-bg`]: v.bg,
      [`--btn-state-${key}-color`]: v.color,
      [`--btn-state-${key}-border`]: v.border
    }
  }
  return { ...build('default'), ...build('hover'), ...build('active') }
})
</script>

<style scoped lang="scss">
.base-btn {
  border: 2px solid transparent;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0;
  text-transform: none;
  color: var(--btn-state-default-color);
  border-color: var(--btn-state-default-border);
  background: var(--btn-state-default-bg);
  transition:
    background 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease;

  &:hover {
    color: var(--btn-state-hover-color);
    border-color: var(--btn-state-hover-border);
    background: var(--btn-state-hover-bg);
  }

  &:active {
    color: var(--btn-state-active-color);
    border-color: var(--btn-state-active-border);
    background: var(--btn-state-active-bg);
  }
}

.base-btn__icon {
  margin-right: 8px;
}

.base-btn--block {
  display: flex;
  width: 100%;
}

.base-btn--lg {
  padding: 13px 30px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 17px;
}

.base-btn--sm {
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 10px;
  line-height: 12px;
}

.base-btn--blue1 {
  --btn-solid: linear-gradient(131.23deg, #093095 5.3%, #030f2f 116%);
  --btn-light: linear-gradient(112.95deg, #3061e2 2.5%, #093095 100%);
  --btn-accent: #093095;
  --btn-accent-fill: linear-gradient(#093095, #093095);
}

.base-btn--blue2 {
  --btn-solid: linear-gradient(131.23deg, #7ea0fa 12.3%, #093095 128.8%);
  --btn-light: linear-gradient(112.95deg, #3061e2 2.5%, #093095 100%);
  --btn-accent: #ffffff;
  --btn-accent-fill: linear-gradient(#ffffff, #ffffff);
}

.base-btn--green {
  --btn-solid: linear-gradient(131.23deg, #73b834 5.3%, #04661f 116%);
  --btn-light: linear-gradient(112.95deg, #98e455 2.5%, #71b634 100%);
  --btn-accent: #8cd64b;
  --btn-accent-fill: linear-gradient(#8cd64b, #8cd64b);
}

.base-btn--red {
  --btn-solid: linear-gradient(131.23deg, #fb2626 5.3%, #7f0326 116%);
  --btn-light: linear-gradient(112.95deg, #fe4b4f 2.5%, #c7072e 100%);
  --btn-accent: #990a26;
  --btn-accent-fill: linear-gradient(#990a26, #990a26);
}

.base-btn--text,
.base-btn--text:hover,
.base-btn--text:active,
.base-btn--text:focus {
  padding: 0;
  min-height: 0;
  border: none;
  background: transparent !important;
  font-size: 14px;
  line-height: 17px;
  color: #2a4ec4;
  text-decoration: underline;
}

.base-btn--text :deep(.q-btn__content) {
  padding: 0;
  margin: 0;
  min-height: 17px;
}

.base-btn--text:hover {
  color: #0f245b;
  text-decoration: underline;
}

.base-btn--text:active {
  color: #7f9ad1;
  text-decoration: none;
}

.base-btn--text :deep(.q-focus-helper) {
  display: none;
}

.base-btn:disabled,
.base-btn.q-btn--disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
