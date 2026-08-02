<template>
  <div
    ref="rootRef"
    :class="[
      'base-select',
      {
        'base-select--open': listVisible,
        'base-select--block': block,
        'base-select--filled': Boolean(modelValue),
        'base-select--disabled': disable
      }
    ]"
  >
    <button
      ref="triggerRef"
      type="button"
      class="base-select__trigger"
      :aria-expanded="open"
      :aria-disabled="disable || undefined"
      :tabindex="disable ? -1 : undefined"
      @click="toggle"
    >
      <span class="base-select__value">{{ currentLabel }}</span>
      <ChevronIcon :direction="open ? 'up' : 'down'" color="var(--dvijok-text-secondary)" />
    </button>

    <Teleport to="body">
      <Transition name="base-select-list" @after-leave="listVisible = false">
        <ul v-if="open" ref="listRef" class="base-select__list" :style="listStyle" @click.stop>
          <li
            v-for="option in options"
            :key="option.value"
            :class="[
              'base-select__option',
              { 'base-select__option--active': isActive(option.value) }
            ]"
            @click="select(option.value)"
          >
            {{ option.label }}
          </li>
        </ul>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
  disable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const triggerRef = ref(null)
const listRef = ref(null)
const open = ref(false)
const listVisible = ref(false)
const listStyle = ref({})

const currentLabel = computed(() => {
  const active = props.options.find(o => o.value === props.modelValue)
  return active ? active.label : props.placeholder
})

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

function select(value) {
  emit('update:modelValue', value)
  open.value = false
}

function updateListPosition() {
  const trigger = triggerRef.value
  if (!trigger || !open.value) return

  const rect = trigger.getBoundingClientRect()
  listStyle.value = {
    position: 'fixed',
    top: `${rect.bottom - 1}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
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
  if (!value) return
  await nextTick()
  updateListPosition()
})

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
  border-radius: 6px;
  background-color: var(--dvijok-white);
  cursor: pointer;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
  text-align: left;
  transition:
    border-bottom-left-radius 0.18s ease,
    border-bottom-right-radius 0.18s ease;
}

.base-select--filled .base-select__trigger {
  color: var(--dvijok-bg-dark);
}

.base-select--disabled .base-select__trigger {
  cursor: default;
  pointer-events: none;
  opacity: 0.6;
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
  border-radius: 0 0 6px 6px;
  background-color: var(--dvijok-white);
  box-sizing: border-box;
  overflow: hidden;
}

.base-select__option {
  padding: 9px;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-bg-dark);
  cursor: pointer;
}

.base-select__option--active {
  background-color: var(--dvijok-choice-active);
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
