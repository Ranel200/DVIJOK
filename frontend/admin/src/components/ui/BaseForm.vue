<template>
  <div class="base-form">
    <div class="base-form__body" :style="bodyStyle">
      <div ref="scrollRef" class="base-form__scroll" :style="scrollStyle" @scroll="updateThumb">
        <BaseFormBlock
          v-for="(block, index) in blocks"
          :key="block.id ?? index"
          :title="block.title"
        >
          <div
            v-for="row in rowsOf(block.fields)"
            :key="row.id"
            :class="['base-form__row', { 'base-form__row--inline': row.inline }]"
          >
            <div
              v-for="field in row.fields"
              :key="field.key"
              class="base-form__field"
              :data-field-key="field.key"
            >
              <BaseField
                v-if="isText(field)"
                :model-value="modelValue[field.key]"
                :label="field.label"
                :placeholder="field.placeholder"
                :type="field.type === 'password' && !visible[field.key] ? 'password' : 'text'"
                :error="Boolean(errors[field.key])"
                :error-message="errors[field.key]"
                :disable="isDisabled(field)"
                block
                @update:model-value="updateField(field, $event)"
              >
                <template v-if="field.type === 'password'" #append>
                  <q-btn
                    flat
                    dense
                    type="button"
                    class="base-form__eye-btn"
                    :aria-label="visible[field.key] ? 'Скрыть пароль' : 'Показать пароль'"
                    @click="toggleVisible(field.key)"
                  >
                    <EyeIcon :closed="visible[field.key]" />
                  </q-btn>
                </template>
              </BaseField>

              <div v-else-if="field.type === 'choice'" class="base-form__choice">
                <span v-if="field.label" class="base-form__label">{{ field.label }}</span>
                <BaseChoice
                  :model-value="modelValue[field.key]"
                  :options="field.options"
                  :shape="field.shape"
                  :block="field.block !== false"
                  :disable="isDisabled(field)"
                  @update:model-value="updateField(field, $event)"
                />
              </div>

              <div v-else-if="field.type === 'consent'" class="base-form__consent">
                <BaseCheckbox
                  :model-value="modelValue[field.key]"
                  :disable="isDisabled(field)"
                  @update:model-value="updateField(field, $event)"
                />
                <p class="base-form__consent-text">
                  Согласен с
                  <button type="button" class="base-form__link">условиями использования</button>
                  и
                  <button type="button" class="base-form__link"
                    >политикой конфиденциальности</button
                  >
                </p>
              </div>

              <div v-else-if="field.type === 'empty'" class="base-form__empty" aria-hidden="true" />
            </div>
          </div>
        </BaseFormBlock>
      </div>

      <div v-show="scrollable" class="base-form__scrollbar" aria-hidden="true">
        <div ref="thumbRef" class="base-form__scrollbar-thumb" :style="thumbStyle" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, onUpdated, reactive, ref } from 'vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  blocks: {
    type: Array,
    default: () => []
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  disable: {
    type: Boolean,
    default: false
  },
  maxHeight: {
    type: [String, Number],
    default: '500px'
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = reactive({})

const scrollRef = ref(null)
const thumbRef = ref(null)
const scrollable = ref(false)
const thumbTop = ref(0)

const thumbStyle = computed(() => ({
  transform: `translateY(${thumbTop.value}px)`
}))

const bodyStyle = computed(() => {
  if (props.maxHeight === null || props.maxHeight === undefined || props.maxHeight === 'none') {
    return { maxHeight: 'none', overflow: 'visible' }
  }
  const value = typeof props.maxHeight === 'number' ? `${props.maxHeight}px` : props.maxHeight
  return { maxHeight: value }
})

const scrollStyle = computed(() => {
  if (props.maxHeight === null || props.maxHeight === undefined || props.maxHeight === 'none') {
    return { overflowY: 'visible' }
  }
  return null
})

const allowScroll = computed(
  () => !(props.maxHeight === null || props.maxHeight === undefined || props.maxHeight === 'none')
)

function isText(field) {
  return !field.type || field.type === 'text' || field.type === 'password'
}

function isDisabled(field) {
  return props.disable || Boolean(field.disable)
}

function toggleVisible(key) {
  visible[key] = !visible[key]
}

function updateField(field, value) {
  if (isDisabled(field)) return
  const next = typeof field.transform === 'function' ? field.transform(value) : value
  emit('update:modelValue', { ...props.modelValue, [field.key]: next })
}

function updateThumb() {
  const el = scrollRef.value
  if (!el || !allowScroll.value) {
    scrollable.value = false
    return
  }
  const trackHeight = el.clientHeight
  const maxScroll = el.scrollHeight - trackHeight
  scrollable.value = maxScroll > 1
  if (!scrollable.value || !thumbRef.value) return
  const thumbHeight = thumbRef.value.offsetHeight
  const ratio = maxScroll > 0 ? el.scrollTop / maxScroll : 0
  thumbTop.value = ratio * (trackHeight - thumbHeight)
}

onMounted(() => {
  nextTick(updateThumb)
  window.addEventListener('resize', updateThumb)
})

onUpdated(() => nextTick(updateThumb))

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateThumb)
})

function rowsOf(fields) {
  const rows = []
  let current = null
  for (const field of fields) {
    if (field.row) {
      if (!current || current.id !== field.row) {
        current = { id: field.row, inline: true, fields: [] }
        rows.push(current)
      }
      current.fields.push(field)
    } else {
      rows.push({ id: field.key, inline: false, fields: [field] })
      current = null
    }
  }
  return rows
}

function findScrollParent(el) {
  let node = el
  while (node && node !== document.body) {
    const style = window.getComputedStyle(node)
    const overflowY = style.overflowY
    if (
      (overflowY === 'auto' || overflowY === 'scroll') &&
      node.scrollHeight > node.clientHeight + 1
    ) {
      return node
    }
    node = node.parentElement
  }
  return null
}

async function focusField(key, { offset = 24 } = {}) {
  await nextTick()
  const root = scrollRef.value
  if (!root) return
  const fieldEl = root.querySelector(`[data-field-key="${key}"]`)
  if (!fieldEl) return

  const scroller = findScrollParent(fieldEl) || root
  const scrollerRect = scroller.getBoundingClientRect()
  const fieldRect = fieldEl.getBoundingClientRect()
  const delta = fieldRect.top - scrollerRect.top - offset
  if (typeof scroller.scrollBy === 'function') {
    scroller.scrollBy({ top: delta, behavior: 'smooth' })
  } else {
    fieldEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const input = fieldEl.querySelector('input, textarea')
  if (input && typeof input.focus === 'function') {
    input.focus()
  }
}

defineExpose({ focusField })
</script>

<style scoped lang="scss">
.base-form {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 100%;
  overflow: hidden;
}

.base-form__body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: row;
  gap: 10px;
  max-height: 500px;
  overflow: hidden;
}

.base-form__scroll {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 40px;
  overflow-y: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.base-form__scrollbar {
  position: relative;
  flex-shrink: 0;
  width: 8px;
  height: 100%;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 5px;
  box-sizing: border-box;
}

.base-form__scrollbar-thumb {
  position: absolute;
  top: 0;
  left: -1px;
  width: 8px;
  height: 60px;
  border-radius: 5px;
  background-color: var(--dvijok-blue-primary);
  box-sizing: border-box;
}

.base-form__row {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.base-form__row--inline {
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 40px;
}

.base-form__field {
  flex: 1;
  display: flex;
  flex-direction: column;
  scroll-margin-top: 24px;
  scroll-margin-bottom: 24px;
}

.base-form__choice {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.base-form__empty {
  width: 100%;
  min-height: 1px;
}

.base-form__label {
  color: var(--dvijok-bg-dark);
  font-size: 14px;
  line-height: 16px;
  text-align: left;
}

.base-form__consent {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.base-form__consent-text {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
  text-align: left;
}

.base-form__link {
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--dvijok-link);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
  text-decoration: underline;
}

.base-form__link:hover {
  color: var(--dvijok-link-hover);
}

.base-form__eye-btn {
  min-height: auto;
  padding: 0;

  :deep(.q-btn__content) {
    padding: 0;
  }
}
</style>
