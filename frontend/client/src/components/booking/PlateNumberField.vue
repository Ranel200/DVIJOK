<template>
  <div class="plate-field">
    <p class="plate-field__label">Номерной знак *</p>
    <BaseChoice v-model="plateType" shape="pill" :options="PLATE_TYPE_OPTIONS" gap="10px" />

    <template v-if="plateType === 'ru'">
      <div class="plate-field__group">
        <p class="plate-field__caption">Основная комбинация</p>
        <div class="plate-field__row">
          <BaseInput
            v-for="(cell, index) in plateMain"
            :key="`main-${index}`"
            :model-value="cell"
            class="plate-field__cell"
            :placeholder="PLATE_MAIN_KINDS[index] === 'letter' ? 'А' : '0'"
            :maxlength="1"
            :input-attrs="{
              inputmode: PLATE_MAIN_KINDS[index] === 'letter' ? 'text' : 'numeric',
              autocomplete: 'off',
              'aria-label': `Символ ${index + 1}`
            }"
            @update:model-value="value => onPlateMain(index, value)"
          />
        </div>
      </div>

      <div class="plate-field__group">
        <p class="plate-field__caption">Код региона</p>
        <div class="plate-field__row">
          <BaseInput
            v-for="(cell, index) in plateRegion"
            :key="`region-${index}`"
            :model-value="cell"
            class="plate-field__cell"
            placeholder="0"
            :maxlength="1"
            :input-attrs="{
              inputmode: 'numeric',
              autocomplete: 'off',
              'aria-label': `Код региона ${index + 1}`
            }"
            @update:model-value="value => onPlateRegion(index, value)"
          />
          <span
            v-for="n in 3"
            :key="`phantom-${n}`"
            class="plate-field__cell plate-field__cell--phantom"
            aria-hidden="true"
          />
        </div>
      </div>
    </template>

    <BaseInput v-else v-model="foreignPlate" placeholder="Введите номер" block />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { PLATE_LETTERS, PLATE_MAIN_KINDS, PLATE_TYPE_OPTIONS } from '@/utils/booking.js'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'ru'
  }
})

const emit = defineEmits(['update:modelValue', 'update:type'])

const plateMain = ref(['', '', '', '', '', ''])
const plateRegion = ref(['', '', ''])
const foreignPlate = ref('')

const plateType = computed({
  get: () => props.type,
  set: value => emit('update:type', value)
})

function emitPlate() {
  const value =
    plateType.value === 'ru'
      ? `${plateMain.value.join('')}${plateRegion.value.join('')}`
      : foreignPlate.value
  emit('update:modelValue', value)
}

function onPlateMain(index, raw) {
  const kind = PLATE_MAIN_KINDS[index]
  let char = String(raw ?? '')
    .slice(-1)
    .toUpperCase()
  if (kind === 'letter') {
    char = PLATE_LETTERS.includes(char) ? char : ''
  } else {
    char = char.replace(/\D/g, '').slice(-1)
  }
  const next = [...plateMain.value]
  next[index] = char
  plateMain.value = next
  emitPlate()
}

function onPlateRegion(index, raw) {
  const char = String(raw ?? '')
    .replace(/\D/g, '')
    .slice(-1)
  const next = [...plateRegion.value]
  next[index] = char
  plateRegion.value = next
  emitPlate()
}

watch(foreignPlate, () => {
  if (plateType.value === 'foreign') emitPlate()
})

watch(plateType, () => {
  emitPlate()
})
</script>

<style scoped lang="scss">
.plate-field {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.plate-field__label {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.plate-field__group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.plate-field__caption {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.plate-field__row {
  display: flex;
  flex-direction: row;
  gap: 5px;
  width: 100%;
}

.plate-field__cell {
  flex: 1 1 0;
  min-width: 0;

  :deep(.q-field__control) {
    justify-content: center;
    padding: 12px 0;
  }

  :deep(.q-field__native) {
    text-align: center;
  }
}

.plate-field__cell--phantom {
  visibility: hidden;
  pointer-events: none;
  border: 1px solid transparent;
  border-radius: 6px;
  box-sizing: border-box;
}
</style>
