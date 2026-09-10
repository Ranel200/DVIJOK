<template>
  <BaseModal
    :model-value="modelValue"
    fit
    compact
    hide-close
    padding="15px 20px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="marker-add">
      <h3 class="marker-add__title">Введите название маркера</h3>

      <BaseInput v-model="name" placeholder="Название маркера" block />

      <div class="marker-add__color">
        <span class="marker-add__color-label">Установите цвет маркера</span>

        <q-color
          v-model="color"
          class="marker-add__picker"
          :style="pickerStyle"
          default-view="spectrum"
          format-model="rgb"
          no-header
          no-footer
        />

        <div class="marker-add__rgb" aria-label="Значения RGB">
          <label class="marker-add__rgb-field">
            <BaseInput
              :model-value="rgb.r"
              type="number"
              class="marker-add__rgb-input"
              @update:model-value="onRgbChange('r', $event)"
            />
            <span class="marker-add__rgb-key">R</span>
          </label>
          <label class="marker-add__rgb-field">
            <BaseInput
              :model-value="rgb.g"
              type="number"
              class="marker-add__rgb-input"
              @update:model-value="onRgbChange('g', $event)"
            />
            <span class="marker-add__rgb-key">G</span>
          </label>
          <label class="marker-add__rgb-field">
            <BaseInput
              :model-value="rgb.b"
              type="number"
              class="marker-add__rgb-input"
              @update:model-value="onRgbChange('b', $event)"
            />
            <span class="marker-add__rgb-key">B</span>
          </label>
        </div>
      </div>

      <div class="marker-add__actions">
        <button type="button" class="marker-add__submit" :disabled="!canAdd" @click="onAdd">
          Добавить
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'

const DEFAULT_COLOR = 'rgb(9, 48, 149)'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'add'])

const name = ref('')
const color = ref(DEFAULT_COLOR)
const rgb = reactive({ r: 9, g: 48, b: 149 })

const canAdd = computed(() => Boolean(name.value.trim()) && Boolean(color.value))

const pickerStyle = computed(() => ({
  '--marker-color': color.value || DEFAULT_COLOR
}))

watch(
  () => props.modelValue,
  open => {
    if (!open) return
    name.value = ''
    color.value = DEFAULT_COLOR
    applyRgbFromColor(DEFAULT_COLOR)
  }
)

watch(color, value => {
  applyRgbFromColor(value)
})

function clampChannel(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return 0
  return Math.min(255, Math.max(0, Math.round(num)))
}

function applyRgbFromColor(value) {
  const match = String(value || '').match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i)
  if (!match) return
  rgb.r = Number(match[1])
  rgb.g = Number(match[2])
  rgb.b = Number(match[3])
}

function onRgbChange(channel, value) {
  rgb[channel] = clampChannel(value)
  color.value = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`
}

function onAdd() {
  if (!canAdd.value) return
  emit('add', {
    name: name.value.trim(),
    color: color.value
  })
  emit('update:modelValue', false)
}
</script>

<style scoped lang="scss">
.marker-add {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 280px;
  max-width: 100%;
}

.marker-add__title,
.marker-add__color-label {
  margin: 0;
  color: #7a82a0;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
}

.marker-add__color {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.marker-add__picker {
  width: 100%;
  max-width: 100%;
  box-shadow: none;
  border-radius: 10px;
  overflow: hidden;

  :deep(.q-color-picker__sliders) {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    box-sizing: border-box;

    &::before {
      content: '';
      flex-shrink: 0;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--marker-color);
      box-sizing: border-box;
      border: 1px solid rgba(9, 48, 149, 0.15);
    }
  }

  :deep(.q-color-picker__sliders .q-slider) {
    flex: 1;
    min-width: 0;
  }
}

.marker-add__rgb {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.marker-add__rgb-field {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
}

.marker-add__rgb-key {
  color: #7a82a0;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  text-align: center;
}

.marker-add__rgb-input {
  width: 48px;

  :deep(.q-field__control) {
    border-radius: 0;
    padding: 8px 4px;
  }

  :deep(.q-field__native) {
    text-align: center;
  }
}

.marker-add__actions {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.marker-add__submit {
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: #093095;

  &:disabled {
    opacity: 0.45;
    cursor: default;
  }

  &:not(:disabled):hover {
    opacity: 0.85;
  }

  &:focus-visible {
    outline: 2px solid #093095;
    outline-offset: 2px;
    border-radius: 4px;
  }
}
</style>
