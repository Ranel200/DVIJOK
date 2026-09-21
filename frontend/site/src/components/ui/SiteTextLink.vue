<template>
  <component
    :is="tag"
    class="site-text-link"
    :to="to || undefined"
    :type="tag === 'button' ? 'button' : undefined"
  >
    <ArrowIcon v-if="direction === 'left'" color="#2E68FF" direction="left" />
    <slot />
    <ArrowIcon v-if="direction === 'right'" color="#2E68FF" direction="right" />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'

const props = defineProps({
  to: {
    type: [String, Object],
    default: null
  },
  direction: {
    type: String,
    default: 'right',
    validator: value => ['left', 'right'].includes(value)
  }
})

const tag = computed(() => (props.to ? 'router-link' : 'button'))
</script>

<style scoped>
.site-text-link {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  font-family: inherit;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #2e68ff;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s ease;
}

.site-text-link:hover {
  color: #3061e2;
}

.site-text-link:active {
  color: #1a4fd9;
}
</style>
