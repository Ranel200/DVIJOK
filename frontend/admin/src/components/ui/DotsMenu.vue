<template>
  <button
    type="button"
    class="dots-menu__trigger"
    aria-label="Действия"
    aria-haspopup="menu"
    :aria-expanded="open"
    @click.stop="toggle"
  >
    <img src="/admin/icons/services/dots.svg" alt="" />
  </button>

  <Teleport to="body">
    <Transition name="dots-menu">
      <div
        v-if="open"
        ref="menuEl"
        class="dots-menu"
        :class="{ 'dots-menu--above': above }"
        role="menu"
        :style="style"
        @click.stop
      >
        <button
          v-for="item in items"
          :key="item.key"
          type="button"
          class="dots-menu__item"
          :class="{ 'dots-menu__item--danger': item.danger }"
          role="menuitem"
          @click="onSelect(item)"
        >
          <div class="dots-menu__icon">
            <img :src="item.icon" alt="" />
          </div>
          <span>{{ item.label }}</span>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  items: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:open', 'select'])

const menuEl = ref(null)
const style = ref({})
const above = ref(false)
let anchorRect = null

function close() {
  if (props.open) emit('update:open', false)
}

function positionMenu(rect) {
  const el = menuEl.value
  if (!el || !rect) return

  const menuRect = el.getBoundingClientRect()
  const gap = 4
  const pad = 8
  const maxTop = window.innerHeight - pad - menuRect.height
  let top = rect.bottom + gap
  let isAbove = false

  if (top > maxTop) {
    top = rect.top - gap - menuRect.height
    isAbove = true
  }

  top = Math.min(Math.max(top, pad), Math.max(pad, maxTop))

  let left = rect.right
  left = Math.min(Math.max(left, pad + menuRect.width), window.innerWidth - pad)

  above.value = isAbove
  style.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

async function toggle(event) {
  if (props.open) {
    close()
    return
  }
  anchorRect = event.currentTarget.getBoundingClientRect()
  above.value = false
  style.value = {
    top: `${anchorRect.bottom + 4}px`,
    left: `${anchorRect.right}px`,
    visibility: 'hidden'
  }
  emit('update:open', true)
  await nextTick()
  positionMenu(anchorRect)
  style.value = { ...style.value, visibility: undefined }
}

function onSelect(item) {
  emit('select', item.key)
  close()
}

function onDocumentClick() {
  close()
}

function onDocumentScroll() {
  close()
}

function onDocumentKeydown(event) {
  if (event.key === 'Escape') close()
}

function bindGlobal() {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('scroll', onDocumentScroll, true)
  document.addEventListener('keydown', onDocumentKeydown)
}

function unbindGlobal() {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('scroll', onDocumentScroll, true)
  document.removeEventListener('keydown', onDocumentKeydown)
}

watch(
  () => props.open,
  async value => {
    if (!value) {
      unbindGlobal()
      return
    }
    await nextTick()
    if (anchorRect) positionMenu(anchorRect)
    bindGlobal()
  }
)

onBeforeUnmount(unbindGlobal)
</script>

<style scoped lang="scss">
.dots-menu__trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.dots-menu__trigger img {
  display: block;
}

.dots-menu {
  position: fixed;
  z-index: 3000;
  transform: translateX(-100%);
  transform-origin: top right;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px;
  box-sizing: border-box;
  background-color: var(--dvijok-white);
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
}

.dots-menu--above {
  transform-origin: bottom right;
}

.dots-menu-enter-active,
.dots-menu-leave-active {
  transition:
    opacity 0.16s ease,
    transform 0.16s ease;
}

.dots-menu-enter-from,
.dots-menu-leave-to {
  opacity: 0;
  transform: translateX(-100%) scale(0.96) translateY(-4px);
}

.dots-menu--above.dots-menu-enter-from,
.dots-menu--above.dots-menu-leave-to {
  transform: translateX(-100%) scale(0.96) translateY(4px);
}

.dots-menu-enter-to,
.dots-menu-leave-from {
  opacity: 1;
  transform: translateX(-100%) scale(1) translateY(0);
}

.dots-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  text-align: left;
  white-space: nowrap;
  font-weight: 400;
  font-size: 12px;
  line-height: 100%;
  color: var(--dvijok-blue-primary);
}

.dots-menu__item--danger {
  color: var(--dvijok-danger-strong);
}

.dots-menu__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.dots-menu__icon img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}
</style>
