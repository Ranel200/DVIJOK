<template>
  <button type="button" class="glass-action-row" @click="emit('click', $event)">
    <div class="glass-action-row__main">
      <slot>
        <img v-if="icon" class="glass-action-row__icon" :src="icon" alt="" />
        <span v-if="label" class="glass-action-row__label">{{ label }}</span>
      </slot>
    </div>
    <slot v-if="showChevron" name="trailing">
      <img
        class="glass-action-row__chevron"
        src="/client/icons/record/chevron-right.svg"
        alt=""
        width="11"
        height="20"
      />
    </slot>
  </button>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  showChevron: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])
</script>

<style scoped lang="scss">
@use '../../css/glass' as glass;

.glass-action-row {
  @include glass.glass-light;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  width: 100%;
  padding: 10px 15px;
  border: none;
  border-radius: 10px;
  box-sizing: border-box;
  cursor: pointer;
  text-align: left;
}

.glass-action-row__main {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
  min-width: 0;
  flex: 1;
}

.glass-action-row__icon {
  display: block;
  flex-shrink: 0;
}

.glass-action-row__label {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-bg-dark);
}

.glass-action-row__chevron {
  display: block;
  flex-shrink: 0;
}
</style>
