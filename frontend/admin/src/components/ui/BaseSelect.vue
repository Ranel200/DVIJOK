<template>
  <div
    ref="rootRef"
    :class="[
      'base-select',
      `base-select--${variant}`,
      {
        'base-select--open': listVisible,
        'base-select--block': block,
        'base-select--center': align === 'center',
        'base-select--no-chevron': hideChevron,
        'base-select--disabled': disable,
        'base-select--error': shownError
      }
    ]"
  >
    <div
      v-if="searchable"
      ref="triggerRef"
      class="base-select__trigger"
      role="combobox"
      :aria-expanded="open"
      :aria-invalid="shownError || undefined"
      :aria-disabled="disable || undefined"
      @click="openSearch"
    >
      <input
        ref="searchInputRef"
        v-model="searchQuery"
        class="base-select__search-input"
        type="text"
        :placeholder="placeholder"
        :disabled="disable"
        autocomplete="off"
        @focus="openSearch"
        @input="openSearch"
        @keydown.enter.prevent="selectFirstFiltered"
        @keydown.esc.prevent="closeSearch"
      />
      <ChevronIcon
        v-if="!hideChevron"
        :direction="open ? 'up' : 'down'"
        @click.stop="toggle"
      />
    </div>
    <button
      v-else
      ref="triggerRef"
      type="button"
      class="base-select__trigger"
      :aria-expanded="open"
      :aria-invalid="shownError || undefined"
      :aria-disabled="disable || undefined"
      :tabindex="disable ? -1 : undefined"
      @click="toggle"
    >
      <span class="base-select__value">{{ currentLabel }}</span>
      <ChevronIcon v-if="!hideChevron" :direction="open ? 'up' : 'down'" />
    </button>
    <p v-if="shownError && shownMessage" class="base-select__error">{{ shownMessage }}</p>

    <Teleport to="body">
      <Transition name="base-select-list" @after-leave="listVisible = false">
        <ul
          v-if="open"
          ref="listRef"
          :class="['base-select__list', `base-select__list--${variant}`]"
          :style="listStyle"
          @click.stop
        >
          <li
            v-for="option in filteredOptions"
            :key="option.value"
            :class="[
              'base-select__option',
              { 'base-select__option--active': isActive(option.value) }
            ]"
            @click="select(option.value)"
          >
            {{ option.label }}
          </li>
          <li v-if="searchable && !filteredOptions.length" class="base-select__empty">
            Подходящие услуги не найдены
          </li>
        </ul>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useFieldError } from '@/composables/useFormValidation.js'
import ChevronIcon from '@/components/ui/ChevronIcon.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: ''
  },
  block: {
    type: Boolean,
    default: false
  },
  hideChevron: {
    type: Boolean,
    default: false
  },
  align: {
    type: String,
    default: 'left',
    validator: value => ['left', 'center'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: value => ['default', 'accent'].includes(value)
  },
  disable: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  requiredMessage: {
    type: String,
    default: ''
  },
  validate: {
    type: Function,
    default: null
  },
  searchable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const { error: shownError, errorMessage: shownMessage } = useFieldError(props)

const rootRef = ref(null)
const triggerRef = ref(null)
const listRef = ref(null)
const searchInputRef = ref(null)
const open = ref(false)
const listVisible = ref(false)
const listStyle = ref({})
const searchQuery = ref('')

const selectedLabel = computed(() => {
  const active = props.options.find(o => o.value === props.modelValue)
  return active?.label || ''
})

const currentLabel = computed(() => selectedLabel.value || props.placeholder)

const filteredOptions = computed(() => {
  const query = normalizeSearch(searchQuery.value)
  if (!props.searchable || !query) return props.options

  const terms = query.split(/\s+/).filter(Boolean)
  return props.options.filter(option => {
    const label = normalizeSearch(option.label)
    return terms.every(term => label.includes(term))
  })
})

function normalizeSearch(value) {
  return String(value ?? '')
    .toLocaleLowerCase('ru-RU')
    .replaceAll('ё', 'е')
    .trim()
}

function isActive(value) {
  return props.modelValue === value
}

function toggle() {
  if (props.disable) return
  open.value = !open.value
  if (open.value) {
    listVisible.value = true
  }
}

function openSearch() {
  if (props.disable) return
  open.value = true
  listVisible.value = true
}

function closeSearch() {
  open.value = false
}

function selectFirstFiltered() {
  const first = filteredOptions.value[0]
  if (open.value && first) select(first.value)
}

function select(value) {
  const option = props.options.find(item => item.value === value)
  emit('update:modelValue', value)
  searchQuery.value = option?.label || ''
  open.value = false
}

function updateListPosition() {
  const trigger = triggerRef.value
  if (!trigger || !open.value) return

  const rect = trigger.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom - 8
  const maxHeight = Math.max(120, Math.min(280, spaceBelow))

  listStyle.value = {
    position: 'fixed',
    top: `${rect.bottom - 1}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    maxHeight: `${maxHeight}px`,
    zIndex: 7000
  }
}

function onDocumentClick(e) {
  if (!open.value) return
  const root = rootRef.value
  const list = listRef.value
  if (root?.contains(e.target) || list?.contains(e.target)) return
  open.value = false
}

function onReposition() {
  if (open.value) updateListPosition()
}

watch(open, async value => {
  if (!value) {
    searchQuery.value = selectedLabel.value
    return
  }
  await nextTick()
  updateListPosition()
  if (props.searchable) {
    searchInputRef.value?.focus()
    searchInputRef.value?.select()
  }
})

watch(
  selectedLabel,
  value => {
    if (!open.value) searchQuery.value = value
  },
  { immediate: true }
)

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  window.addEventListener('resize', onReposition)
  window.addEventListener('scroll', onReposition, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
  window.removeEventListener('resize', onReposition)
  window.removeEventListener('scroll', onReposition, true)
})
</script>

<style scoped lang="scss">
.base-select {
  position: relative;
  display: inline-block;
}

.base-select--block {
  display: block;
  width: 100%;
}

.base-select__trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 9px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 8px;
  background-color: var(--dvijok-white);
  cursor: pointer;
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;
  color: var(--dvijok-text-secondary);
  text-align: left;
  transition:
    border-bottom-left-radius 0.18s ease,
    border-bottom-right-radius 0.18s ease;
}

.base-select--center .base-select__trigger {
  justify-content: center;
  text-align: center;
}

.base-select--no-chevron .base-select__value {
  width: 100%;
}

.base-select--disabled .base-select__trigger {
  cursor: default;
  pointer-events: none;
}

.base-select--error .base-select__trigger {
  border-color: var(--dvijok-danger, #c10015);
}

.base-select__error {
  margin: 5px 0 0;
  color: var(--dvijok-danger, #c10015);
  font-size: 12px;
  line-height: 15px;
}

.base-select--open .base-select__trigger {
  border-bottom-color: transparent;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.base-select__value {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.base-select__list {
  list-style: none;
  margin: 0;
  padding: 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid var(--dvijok-text-secondary);
  border-top: none;
  border-radius: 0 0 8px 8px;
  background-color: var(--dvijok-white);
  box-sizing: border-box;
  overflow-x: hidden;
  overflow-y: auto;
}

.base-select__option {
  padding: 10px 9px;
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;
  color: var(--dvijok-text-primary);
  cursor: pointer;
}

.base-select__search-input {
  flex: 1;
  min-width: 0;
  padding: 0;
  border: 0;
  outline: none;
  color: var(--dvijok-text-primary);
  background: transparent;
  font: inherit;
}

.base-select__search-input::placeholder,
.base-select__empty {
  color: var(--dvijok-text-secondary);
}

.base-select__empty {
  padding: 10px 9px;
  font-size: 12px;
  line-height: 15px;
}

.base-select__option--active {
  background-color: var(--dvijok-choice-active);
}

.base-select--accent .base-select__trigger {
  border-color: var(--dvijok-text-primary);
  background-color: var(--dvijok-choice-active);
  color: var(--dvijok-text-primary);
}

.base-select--accent .base-select__trigger :deep(.chevron-icon) {
  color: var(--dvijok-text-primary);
}

.base-select__list--accent {
  border-color: var(--dvijok-text-primary);
  background-color: var(--dvijok-choice-active);
}

.base-select__list--accent .base-select__option--active {
  background-color: var(--dvijok-white);
  color: var(--dvijok-text-primary);
}

.base-select-list-enter-active,
.base-select-list-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.base-select-list-enter-from,
.base-select-list-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
