<template>
  <div class="plate-field">
    <p class="plate-field__label">
      Номерной знак<span class="plate-field__required" aria-hidden="true"> *</span>
    </p>
    <BaseChoice v-model="plateType" shape="pill" :options="PLATE_TYPE_OPTIONS" gap="10px" />

    <template v-if="plateType === 'ru'">
      <div class="plate-field__group">
        <p class="plate-field__caption">Основная комбинация</p>
        <div class="plate-field__row">
          <BaseInput
            v-for="(cell, index) in plateMain"
            :key="`main-${index}`"
            :ref="el => setMainRef(el, index)"
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
            @keydown="event => onMainKeydown(index, event)"
            @paste="event => onPaste(event, 'main', index)"
          />
        </div>
      </div>

      <div class="plate-field__group">
        <p class="plate-field__caption">Код региона</p>
        <div class="plate-field__row">
          <BaseInput
            v-for="(cell, index) in plateRegion"
            :key="`region-${index}`"
            :ref="el => setRegionRef(el, index)"
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
            @keydown="event => onRegionKeydown(index, event)"
            @paste="event => onPaste(event, 'region', index)"
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
const syncing = ref(false)
const mainRefs = ref([])
const regionRefs = ref([])

const plateType = computed({
  get: () => props.type,
  set: value => emit('update:type', value)
})

function setMainRef(el, index) {
  mainRefs.value[index] = el
}

function setRegionRef(el, index) {
  regionRefs.value[index] = el
}

function focusField(field) {
  const native = field?.$el?.querySelector?.('input')
  native?.focus?.()
  native?.select?.()
}

function focusMain(index) {
  focusField(mainRefs.value[index])
}

function focusRegion(index) {
  focusField(regionRefs.value[index])
}

function emitPlate() {
  if (syncing.value) return
  const value =
    plateType.value === 'ru'
      ? `${plateMain.value.join('')}${plateRegion.value.join('')}`
      : foreignPlate.value
  emit('update:modelValue', value)
}

function applyExternalValue(raw, type) {
  const cleaned = String(raw ?? '')
    .replace(/\s/g, '')
    .toUpperCase()
  syncing.value = true
  if (type === 'foreign') {
    foreignPlate.value = String(raw ?? '')
    plateMain.value = ['', '', '', '', '', '']
    plateRegion.value = ['', '', '']
  } else {
    const main = cleaned.slice(0, 6).padEnd(6, ' ').slice(0, 6)
    const region = cleaned.slice(6, 9).padEnd(3, ' ').slice(0, 3)
    plateMain.value = main.split('').map(ch => (ch === ' ' ? '' : ch))
    plateRegion.value = region.split('').map(ch => (ch === ' ' ? '' : ch))
    foreignPlate.value = ''
  }
  syncing.value = false
}

function sanitizeMainChar(index, raw) {
  const kind = PLATE_MAIN_KINDS[index]
  let char = String(raw ?? '')
    .slice(-1)
    .toUpperCase()
  if (kind === 'letter') {
    return PLATE_LETTERS.includes(char) ? char : ''
  }
  return char.replace(/\D/g, '').slice(-1)
}

function sanitizeRegionChar(raw) {
  return String(raw ?? '')
    .replace(/\D/g, '')
    .slice(-1)
}

function onPlateMain(index, raw) {
  const char = sanitizeMainChar(index, raw)
  const next = [...plateMain.value]
  next[index] = char
  plateMain.value = next
  emitPlate()
  if (!char) return
  if (index < plateMain.value.length - 1) {
    focusMain(index + 1)
    return
  }
  focusRegion(0)
}

function onPlateRegion(index, raw) {
  const char = sanitizeRegionChar(raw)
  const next = [...plateRegion.value]
  next[index] = char
  plateRegion.value = next
  emitPlate()
  if (char && index < plateRegion.value.length - 1) {
    focusRegion(index + 1)
  }
}

function onMainKeydown(index, event) {
  if (event.key !== 'Backspace') return
  if (plateMain.value[index]) return
  if (index === 0) return
  event.preventDefault()
  const next = [...plateMain.value]
  next[index - 1] = ''
  plateMain.value = next
  emitPlate()
  focusMain(index - 1)
}

function onRegionKeydown(index, event) {
  if (event.key !== 'Backspace') return
  if (plateRegion.value[index]) return
  event.preventDefault()
  if (index > 0) {
    const next = [...plateRegion.value]
    next[index - 1] = ''
    plateRegion.value = next
    emitPlate()
    focusRegion(index - 1)
    return
  }
  const next = [...plateMain.value]
  next[next.length - 1] = ''
  plateMain.value = next
  emitPlate()
  focusMain(plateMain.value.length - 1)
}

function onPaste(event, group, startIndex) {
  const text = event.clipboardData?.getData('text') || ''
  if (!text) return

  event.preventDefault()

  const main = [...plateMain.value]
  const region = [...plateRegion.value]
  let cursor = group === 'main' ? startIndex : plateMain.value.length + startIndex
  let focusIndex = cursor

  for (const raw of text.replace(/\s/g, '')) {
    if (cursor >= main.length + region.length) break
    if (cursor < main.length) {
      const char = sanitizeMainChar(cursor, raw)
      if (!char) continue
      main[cursor] = char
    } else {
      const char = sanitizeRegionChar(raw)
      if (!char) continue
      region[cursor - main.length] = char
    }
    cursor += 1
    focusIndex = cursor
  }

  plateMain.value = main
  plateRegion.value = region
  emitPlate()

  const maxIndex = main.length + region.length - 1
  const nextFocus = Math.min(focusIndex, maxIndex)
  if (nextFocus < main.length) {
    focusMain(nextFocus)
  } else {
    focusRegion(nextFocus - main.length)
  }
}

watch(foreignPlate, () => {
  if (plateType.value === 'foreign') emitPlate()
})

watch(plateType, () => {
  emitPlate()
})

watch(
  () => [props.modelValue, props.type],
  ([value, type]) => {
    const current =
      type === 'ru'
        ? `${plateMain.value.join('')}${plateRegion.value.join('')}`
        : foreignPlate.value
    const normalized =
      type === 'ru'
        ? String(value ?? '')
            .replace(/\s/g, '')
            .toUpperCase()
        : String(value ?? '')
    if (normalized === current) return
    applyExternalValue(value, type)
  },
  { immediate: true }
)
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

.plate-field__required {
  color: var(--dvijok-danger);
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
