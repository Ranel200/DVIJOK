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
    <span v-if="$slots.prepend" class="base-btn__prepend">
      <slot name="prepend" />
    </span>
    <q-icon v-if="icon" :name="icon" size="1.2em" class="base-btn__icon" />
    <slot />
    <span v-if="$slots.append" class="base-btn__append">
      <slot name="append" />
    </span>
  </q-btn>
</template>

<script setup>
import { computed } from 'vue'
import { BUTTON_SCHEMES, DEFAULT_BUTTON_SCHEME } from './buttonSchemes.js'

const VARIANT_STYLE = {
  solid: { bg: 'var(--btn-solid)', color: 'var(--dvijok-white)', border: 'transparent' },
  light: { bg: 'var(--btn-light)', color: 'var(--dvijok-white)', border: 'transparent' },
  accent: {
    bg: 'var(--btn-accent-fill)',
    color: 'var(--dvijok-white)',
    border: 'transparent'
  },
  outlined: {
    bg: 'transparent',
    color: 'var(--btn-accent)',
    border: 'var(--btn-accent)'
  },
  outlinedWhite: {
    bg: 'var(--dvijok-white)',
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
  },
  iconSpacing: {
    type: [Number, String],
    default: null
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
  const spacing =
    props.iconSpacing === null || props.iconSpacing === undefined
      ? null
      : typeof props.iconSpacing === 'number'
        ? `${props.iconSpacing}px`
        : props.iconSpacing
  return {
    ...build('default'),
    ...build('hover'),
    ...build('active'),
    ...(spacing ? { '--btn-icon-spacing': spacing } : {})
  }
})
</script>

<style scoped lang="scss">
.base-btn {
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0;
  text-transform: none;
  color: var(--btn-state-default-color);
  box-shadow: inset 0 0 0 2px var(--btn-state-default-border);
  background: var(--btn-state-default-bg);
  transition:
    background 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease;

  &:not(:disabled):not(.q-btn--disabled):hover {
    color: var(--btn-state-hover-color);
    box-shadow: inset 0 0 0 2px var(--btn-state-hover-border);
    background: var(--btn-state-hover-bg);
  }

  &:not(:disabled):not(.q-btn--disabled):active {
    color: var(--btn-state-active-color);
    box-shadow: inset 0 0 0 2px var(--btn-state-active-border);
    background: var(--btn-state-active-bg);
  }
}

.base-btn__icon {
  margin-right: var(--btn-icon-spacing, 8px);
}

.base-btn__prepend {
  display: inline-flex;
  margin-right: var(--btn-icon-spacing, 8px);
}

.base-btn__append {
  display: inline-flex;
  margin-left: var(--btn-icon-spacing, 8px);
}

.base-btn--block {
  display: flex;
  width: 100%;
}

.base-btn--lg {
  padding: 15px 32px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 17px;
}

.base-btn--sm {
  padding: 12px 22px;
  border-radius: 50px;
  font-size: 10px;
  line-height: 12px;
}

.base-btn--blue1 {
  --btn-solid: linear-gradient(131.23deg, var(--dvijok-blue-primary) 5.3%, #030f2f 116%);
  --btn-light: linear-gradient(
    112.95deg,
    var(--dvijok-blue-light) 2.5%,
    var(--dvijok-blue-primary) 100%
  );
  --btn-accent: var(--dvijok-blue-primary);
  --btn-accent-fill: linear-gradient(var(--dvijok-blue-primary), var(--dvijok-blue-primary));
}

.base-btn--blue2 {
  --btn-solid: linear-gradient(
    131.23deg,
    var(--dvijok-blue-pale) 12.3%,
    var(--dvijok-blue-primary) 128.8%
  );
  --btn-light: linear-gradient(
    112.95deg,
    var(--dvijok-blue-light) 2.5%,
    var(--dvijok-blue-primary) 100%
  );
  --btn-accent: var(--dvijok-white);
  --btn-accent-fill: linear-gradient(var(--dvijok-white), var(--dvijok-white));
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
  box-shadow: none;
  background: transparent !important;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link);
  text-decoration: underline;
}

.base-btn--text :deep(.q-btn__content) {
  padding: 0;
  margin: 0;
  min-height: 17px;
}

.base-btn--text:hover {
  color: var(--dvijok-link-hover);
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
  transition: none;
  pointer-events: none;
}
</style>
