<template>
  <div
    v-if="isWrapper"
    :class="[
      'base-scrollbar',
      `base-scrollbar--${orientation}`,
      { 'base-scrollbar--disabled': !enabled }
    ]"
  >
    <div
      v-if="trackPosition === 'start'"
      v-show="scrollable"
      ref="trackRef"
      :class="trackClass"
      aria-hidden="true"
      @pointerdown="onTrackPointerDown"
    >
      <div
        ref="thumbRef"
        :class="thumbClass"
        :style="thumbStyle"
        @pointerdown="onThumbPointerDown"
      />
    </div>

    <div class="base-scrollbar__viewport">
      <slot
        name="overlay"
        :scrollable="scrollable"
        :can-scroll-start="canScrollStart"
        :can-scroll-end="canScrollEnd"
      />
      <div
        ref="scrollRef"
        :class="['base-scrollbar__content', contentClass]"
        :style="contentStyle"
        @scroll="updateThumb"
      >
        <slot />
      </div>
    </div>

    <div
      v-if="trackPosition === 'end'"
      v-show="scrollable"
      ref="trackRef"
      :class="trackClass"
      aria-hidden="true"
      @pointerdown="onTrackPointerDown"
    >
      <div
        ref="thumbRef"
        :class="thumbClass"
        :style="thumbStyle"
        @pointerdown="onThumbPointerDown"
      />
    </div>
  </div>

  <div
    v-else
    v-show="scrollable"
    ref="trackRef"
    :class="trackClass"
    aria-hidden="true"
    @pointerdown="onTrackPointerDown"
  >
    <div ref="thumbRef" :class="thumbClass" :style="thumbStyle" @pointerdown="onThumbPointerDown" />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, unref, watch } from 'vue'

const emit = defineEmits(['update:scrollable', 'update:canScrollStart', 'update:canScrollEnd'])

const props = defineProps({
  orientation: {
    type: String,
    default: 'vertical',
    validator: value => ['vertical', 'horizontal'].includes(value)
  },
  trackPosition: {
    type: String,
    default: 'end',
    validator: value => ['start', 'end'].includes(value)
  },
  scrollTarget: {
    type: Object,
    default: null
  },
  trackOnly: {
    type: Boolean,
    default: false
  },
  enabled: {
    type: Boolean,
    default: true
  },
  contentClass: {
    type: [String, Array, Object],
    default: ''
  },
  contentStyle: {
    type: Object,
    default: null
  }
})

const scrollRef = ref(null)
const trackRef = ref(null)
const thumbRef = ref(null)
const scrollable = ref(false)
const thumbOffset = ref(0)
const thumbDragging = ref(false)
const canScrollStart = ref(false)
const canScrollEnd = ref(false)
let thumbDragOffset = 0
let boundTarget = null

const isVertical = computed(() => props.orientation === 'vertical')
const isWrapper = computed(() => !props.trackOnly && !props.scrollTarget)

const trackClass = computed(() => [
  'base-scrollbar__track',
  `base-scrollbar__track--${props.orientation}`,
  { 'base-scrollbar__track--dragging': thumbDragging.value }
])

const thumbClass = computed(() => [
  'base-scrollbar__thumb',
  `base-scrollbar__thumb--${props.orientation}`,
  { 'base-scrollbar__thumb--dragging': thumbDragging.value }
])

const thumbStyle = computed(() =>
  isVertical.value
    ? { transform: `translateY(${thumbOffset.value}px)` }
    : { transform: `translateX(${thumbOffset.value}px)` }
)

function resolveScrollEl() {
  if (props.scrollTarget) return unref(props.scrollTarget)
  return scrollRef.value
}

async function updateThumb() {
  const el = resolveScrollEl()
  if (!el || !props.enabled) {
    scrollable.value = false
    canScrollStart.value = false
    canScrollEnd.value = false
    return
  }

  const clientSize = isVertical.value ? el.clientHeight : el.clientWidth
  const scrollSize = isVertical.value ? el.scrollHeight : el.scrollWidth
  const scrollPos = isVertical.value ? el.scrollTop : el.scrollLeft
  const maxScroll = scrollSize - clientSize
  const wasScrollable = scrollable.value
  scrollable.value = maxScroll > 1

  if (!scrollable.value) {
    canScrollStart.value = false
    canScrollEnd.value = false
    return
  }

  if (!wasScrollable) await nextTick()
  const thumb = thumbRef.value
  if (!thumb) return

  const track = trackRef.value
  const trackSize = track ? (isVertical.value ? track.clientHeight : track.clientWidth) : clientSize
  const thumbSize = isVertical.value ? thumb.offsetHeight : thumb.offsetWidth
  const ratio = maxScroll > 0 ? scrollPos / maxScroll : 0
  thumbOffset.value = ratio * Math.max(0, trackSize - thumbSize)
  canScrollStart.value = scrollPos > 1
  canScrollEnd.value = scrollPos < maxScroll - 1
}

function setScrollByThumbOffset(nextOffset) {
  const el = resolveScrollEl()
  const track = trackRef.value
  const thumb = thumbRef.value
  if (!el || !track || !thumb) return

  const trackSize = isVertical.value ? track.clientHeight : track.clientWidth
  const thumbSize = isVertical.value ? thumb.offsetHeight : thumb.offsetWidth
  const maxThumbOffset = Math.max(0, trackSize - thumbSize)
  const clamped = Math.min(maxThumbOffset, Math.max(0, nextOffset))
  const clientSize = isVertical.value ? el.clientHeight : el.clientWidth
  const scrollSize = isVertical.value ? el.scrollHeight : el.scrollWidth
  const maxScroll = scrollSize - clientSize
  const nextScroll = maxThumbOffset > 0 ? (clamped / maxThumbOffset) * maxScroll : 0

  if (isVertical.value) el.scrollTop = nextScroll
  else el.scrollLeft = nextScroll
}

function onThumbPointerMove(event) {
  if (!thumbDragging.value) return
  const track = trackRef.value
  if (!track) return
  const trackRect = track.getBoundingClientRect()
  const pointer = isVertical.value ? event.clientY : event.clientX
  const trackStart = isVertical.value ? trackRect.top : trackRect.left
  setScrollByThumbOffset(pointer - trackStart - thumbDragOffset)
}

function onThumbPointerUp(event) {
  if (!thumbDragging.value) return
  thumbDragging.value = false
  const thumb = thumbRef.value
  if (thumb && event?.pointerId != null && thumb.hasPointerCapture?.(event.pointerId)) {
    thumb.releasePointerCapture(event.pointerId)
  }
  window.removeEventListener('pointermove', onThumbPointerMove)
  window.removeEventListener('pointerup', onThumbPointerUp)
}

function onThumbPointerDown(event) {
  event.preventDefault()
  event.stopPropagation()
  const thumb = thumbRef.value
  if (!thumb) return
  thumbDragging.value = true
  const thumbRect = thumb.getBoundingClientRect()
  thumbDragOffset = isVertical.value
    ? event.clientY - thumbRect.top
    : event.clientX - thumbRect.left
  thumb.setPointerCapture?.(event.pointerId)
  window.addEventListener('pointermove', onThumbPointerMove)
  window.addEventListener('pointerup', onThumbPointerUp)
}

function onTrackPointerDown(event) {
  if (event.target !== trackRef.value) return
  const track = trackRef.value
  const thumb = thumbRef.value
  if (!track || !thumb) return
  const trackRect = track.getBoundingClientRect()
  const thumbSize = isVertical.value ? thumb.offsetHeight : thumb.offsetWidth
  const pointer = isVertical.value ? event.clientY : event.clientX
  const trackStart = isVertical.value ? trackRect.top : trackRect.left
  setScrollByThumbOffset(pointer - trackStart - thumbSize / 2)
}

function bindTarget(el) {
  if (boundTarget === el) return
  if (boundTarget) boundTarget.removeEventListener('scroll', updateThumb)
  boundTarget = el || null
  if (boundTarget) boundTarget.addEventListener('scroll', updateThumb)
}

watch(scrollable, value => emit('update:scrollable', value))
watch(canScrollStart, value => emit('update:canScrollStart', value))
watch(canScrollEnd, value => emit('update:canScrollEnd', value))

watch(
  () => [unref(props.scrollTarget), props.enabled, props.orientation],
  () => {
    if (props.scrollTarget) bindTarget(unref(props.scrollTarget))
    else bindTarget(null)
    nextTick(updateThumb)
  },
  { flush: 'post' }
)

onMounted(() => {
  if (props.scrollTarget) bindTarget(unref(props.scrollTarget))
  window.addEventListener('resize', updateThumb)
  nextTick(updateThumb)
})

onBeforeUnmount(() => {
  onThumbPointerUp()
  bindTarget(null)
  window.removeEventListener('resize', updateThumb)
})

defineExpose({
  update: updateThumb,
  getScrollEl: resolveScrollEl,
  scrollRef,
  scrollable,
  canScrollStart,
  canScrollEnd
})
</script>

<style scoped lang="scss">
.base-scrollbar {
  display: flex;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  gap: 10px;
}

.base-scrollbar--vertical {
  flex-direction: row;
  align-items: stretch;
}

.base-scrollbar--horizontal {
  flex-direction: column;
}

.base-scrollbar__viewport {
  position: relative;
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
}

.base-scrollbar__content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.base-scrollbar--vertical .base-scrollbar__content {
  overflow-x: hidden;
  overflow-y: auto;
}

.base-scrollbar--horizontal .base-scrollbar__content {
  overflow-x: auto;
  overflow-y: hidden;
}

.base-scrollbar__track {
  position: relative;
  flex-shrink: 0;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 5px;
  box-sizing: border-box;
  cursor: pointer;
  touch-action: none;
}

.base-scrollbar__track--vertical {
  width: 8px;
  height: 100%;
}

.base-scrollbar__track--horizontal {
  width: 100%;
  height: 8px;
}

.base-scrollbar__thumb {
  position: absolute;
  border-radius: 5px;
  background-color: var(--base-scrollbar-thumb, var(--dvijok-blue-primary));
  box-sizing: border-box;
  cursor: grab;
  touch-action: none;
}

.base-scrollbar__thumb--vertical {
  top: 0;
  left: -1px;
  width: 8px;
  height: 60px;
}

.base-scrollbar__thumb--horizontal {
  top: -1px;
  left: 0;
  width: 60px;
  height: 8px;
}

.base-scrollbar__thumb--dragging {
  cursor: grabbing;
}
</style>
