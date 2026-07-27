<template>
  <BaseModal
    :model-value="modelValue"
    fit
    compact
    hide-close
    padding="15px 20px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="staff-color-picker">
      <h3 class="staff-color-picker__title">Выберите цвет сотруднику</h3>

      <div class="staff-color-picker__grid">
        <button
          v-for="item in STAFF_COLORS"
          :key="item.value"
          type="button"
          class="staff-color-picker__item"
          @click="draft = item.value"
        >
          <Radio v-if="draft === item.value" filled :color="item.value" :size="20" />
          <span v-else class="staff-color-picker__dot" :style="{ backgroundColor: item.value }" />
          <span class="staff-color-picker__name">{{ item.label }}</span>
        </button>
      </div>

      <div class="staff-color-picker__actions">
        <BaseButton text :underline="false" color="blue1" @click="onSave">Сохранить</BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import Radio from '@/components/ui/Radio.vue'
import { STAFF_COLORS } from '@/constants/staff.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const draft = ref('')

watch(
  () => [props.modelValue, props.color],
  ([open]) => {
    if (!open) return
    draft.value = props.color || ''
  }
)

function onSave() {
  emit('save', draft.value)
  emit('update:modelValue', false)
}
</script>

<style scoped lang="scss">
.staff-color-picker {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.staff-color-picker__title {
  margin: 0;
  color: #7a82a0;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
}

.staff-color-picker__grid {
  display: grid;
  grid-template-columns: repeat(4, 90px);
  gap: 5px;
  justify-content: start;
}

.staff-color-picker__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  width: 90px;
  padding: 15px 10px;
  box-sizing: border-box;
  border: none;
  border-radius: 20px;
  background: transparent;
  cursor: pointer;

  &:hover,
  &:focus,
  &:active,
  &:focus-visible {
    background: transparent;
    outline: none;
  }
}

.staff-color-picker__dot {
  display: block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  flex-shrink: 0;
}

.staff-color-picker__name {
  color: #7a82a0;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  text-align: center;
}

.staff-color-picker__actions {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
</style>
