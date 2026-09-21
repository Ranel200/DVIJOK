<template>
  <component
    :is="tag"
    class="site-btn"
    :class="[`site-btn--${variant}`, { 'site-btn--stretch': stretch }]"
    :style="widthStyle"
    :to="to || undefined"
    :type="tag === 'button' ? type : undefined"
  >
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: value => ['primary', 'outline'].includes(value)
  },
  to: {
    type: [String, Object],
    default: null
  },
  type: {
    type: String,
    default: 'button'
  },
  stretch: {
    type: Boolean,
    default: false
  },
  width: {
    type: [Number, String],
    default: null
  }
})

const tag = computed(() => (props.to ? 'router-link' : 'button'))

const widthStyle = computed(() => {
  if (props.width == null || props.width === '') return undefined
  const value = typeof props.width === 'number' ? `${props.width}px` : props.width
  return { width: value, flex: 'none' }
})
</script>

<style scoped>
.site-btn {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  border: none;
  font-family: inherit;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
}

.site-btn--stretch {
  flex: 1;
}

.site-btn--primary {
  padding: 15px;
  background: var(--dvijok-blue-bright);
  color: var(--dvijok-white);
}

.site-btn--outline {
  padding: 14px;
  border: 1px solid #000;
  background: transparent;
  color: #000;
}
</style>
