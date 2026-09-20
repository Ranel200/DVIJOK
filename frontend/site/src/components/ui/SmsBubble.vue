<template>
  <div class="sms-bubble" :class="[`sms-bubble--${side}`, `sms-bubble--${color}`]">
    <span
      v-if="side === 'left'"
      class="sms-bubble__tail sms-bubble__tail--bottom-right"
      aria-hidden="true"
    />
    <div class="sms-bubble__body">
      <slot />
    </div>
    <span
      v-if="side === 'right'"
      class="sms-bubble__tail sms-bubble__tail--bottom-left"
      aria-hidden="true"
    />
  </div>
</template>

<script setup>
defineProps({
  side: {
    type: String,
    default: 'left',
    validator: value => ['left', 'right'].includes(value)
  },
  color: {
    type: String,
    default: 'blue',
    validator: value => ['blue', 'gray'].includes(value)
  }
})
</script>

<style scoped>
.sms-bubble {
  display: inline-flex;
  flex-direction: row;
  align-items: flex-end;
  filter: drop-shadow(0 4px 4px #00000040);
}

.sms-bubble__tail {
  position: relative;
  z-index: 1;
  flex: none;
  width: 28px;
  height: 26px;
}

.sms-bubble__tail--bottom-right {
  clip-path: polygon(0 100%, 100% 0, 100% 100%);
}

.sms-bubble__tail--bottom-left {
  clip-path: polygon(0 0, 0 100%, 100% 100%);
}

.sms-bubble__body {
  position: relative;
  z-index: 0;
  box-sizing: border-box;
  flex: 1;
  width: 100%;
  min-width: 0;
  padding: 12px;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  white-space: pre-line;
  box-shadow: 4px 0 4px 0 #00000040;
}

.sms-bubble--blue .sms-bubble__tail,
.sms-bubble--blue .sms-bubble__body {
  background: #2e68ff;
}

.sms-bubble--blue .sms-bubble__body {
  color: #fff;
}

.sms-bubble--gray .sms-bubble__tail,
.sms-bubble--gray .sms-bubble__body {
  background: #d9d9d9;
}

.sms-bubble--gray .sms-bubble__body {
  color: #000;
}
</style>
