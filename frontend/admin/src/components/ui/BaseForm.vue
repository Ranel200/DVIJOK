<template>
  <div :class="['base-form', { 'base-form--horizontal': layout === 'horizontal' }]">
    <BaseScrollbar
      ref="scrollbarRef"
      class="base-form__body"
      content-class="base-form__scroll"
      :content-style="scrollStyle"
      :enabled="allowScroll"
      :style="bodyStyle"
    >
      <BaseFormBlock
        v-for="(block, index) in blocks"
        :key="block.id ?? index"
        :title="block.title"
        :layout="layout"
      >
        <div
          v-for="row in rowsOf(block.fields)"
          :key="row.id"
          :class="[
            'base-form__row',
            {
              'base-form__row--inline': row.inline,
              'base-form__row--horizontal': layout === 'horizontal'
            }
          ]"
        >
          <div
            v-for="field in row.fields"
            :key="field.key"
            :class="[
              'base-form__field',
              { 'base-form__field--horizontal': layout === 'horizontal' }
            ]"
            :data-field-key="field.key"
          >
            <BaseField
              v-if="isText(field)"
              :model-value="modelValue[field.key]"
              :label="field.label"
              :placeholder="field.placeholder"
              :type="fieldType(field)"
              :layout="layout"
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

            <div
              v-else-if="field.type === 'choice'"
              :class="[
                'base-form__choice',
                { 'base-form__choice--horizontal': layout === 'horizontal' }
              ]"
            >
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

            <div
              v-else-if="field.type === 'select'"
              :class="[
                'base-form__select',
                { 'base-form__select--horizontal': layout === 'horizontal' }
              ]"
            >
              <span v-if="field.label" class="base-form__label">{{ field.label }}</span>
              <BaseSelect
                :model-value="modelValue[field.key]"
                :options="field.options"
                :placeholder="field.placeholder"
                :hide-chevron="field.hideChevron"
                :align="field.align"
                :block="field.block !== false"
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
                <button type="button" class="base-form__link">политикой конфиденциальности</button>
              </p>
            </div>

            <div v-else-if="field.type === 'empty'" class="base-form__empty" aria-hidden="true" />
          </div>
        </div>
      </BaseFormBlock>
    </BaseScrollbar>
  </div>
</template>

<script setup>
import { computed, nextTick, onUpdated, reactive, ref } from 'vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseScrollbar from '@/components/ui/BaseScrollbar.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
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
  layout: {
    type: String,
    default: 'vertical',
    validator: value => ['vertical', 'horizontal'].includes(value)
  },
  maxHeight: {
    type: [String, Number],
    default: '500px'
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = reactive({})
const scrollbarRef = ref(null)

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
  return (
    !field.type ||
    field.type === 'text' ||
    field.type === 'password' ||
    field.type === 'textarea' ||
    field.type === 'number'
  )
}

function fieldType(field) {
  if (field.type === 'password') {
    return visible[field.key] ? 'text' : 'password'
  }
  if (field.type === 'textarea' || field.type === 'number') {
    return field.type
  }
  return 'text'
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

onUpdated(() => nextTick(() => scrollbarRef.value?.update()))

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
  const root = scrollbarRef.value?.getScrollEl?.()
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

.base-form--horizontal {
  --dvijok-form-block-title: var(--dvijok-white);
  --dvijok-form-label: var(--dvijok-text-secondary);
}

.base-form__body {
  flex: 1;
  min-height: 0;
  max-height: 500px;
}

.base-form__body :deep(.base-form__scroll) {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.base-form--horizontal .base-form__body :deep(.base-form__scroll) {
  gap: 30px;
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

.base-form__row--horizontal {
  display: contents;
}

.base-form__field--horizontal {
  display: contents;
}

.base-form__choice,
.base-form__select {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.base-form__choice--horizontal,
.base-form__select--horizontal {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.base-form__choice--horizontal .base-form__label,
.base-form__select--horizontal .base-form__label {
  grid-column: 1;
}

.base-form__choice--horizontal :deep(.base-choice),
.base-form__select--horizontal :deep(.base-select) {
  grid-column: 2;
  min-width: 0;
  width: 100%;
}

.base-form__empty {
  width: 100%;
  min-height: 1px;
}

.base-form__label {
  color: var(--dvijok-form-label, var(--dvijok-text-secondary));
  font-size: 14px;
  line-height: 16px;
  text-align: left;
  white-space: nowrap;
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
