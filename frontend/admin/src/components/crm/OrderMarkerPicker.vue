<template>
  <div class="order-marker-picker-wrap" :class="{ 'order-marker-picker-wrap--light': light }">
    <div class="order-marker-picker">
      <div class="order-marker-picker__list" role="listbox" aria-label="Маркеры">
        <button
          v-for="marker in markers"
          :key="marker.id"
          type="button"
          class="order-marker-chip"
          :class="{ 'order-marker-chip--selected': modelValue === marker.id }"
          role="option"
          :aria-selected="modelValue === marker.id"
          :disabled="readonly"
          @click="selectMarker(marker.id)"
        >
          <span
            class="order-marker-chip__dot"
            :style="{ backgroundColor: marker.color }"
            aria-hidden="true"
          />
          <span class="order-marker-chip__name">{{ marker.name }}</span>
        </button>
      </div>
      <button
        v-if="!readonly"
        type="button"
        class="order-marker-picker__add"
        aria-label="Добавить маркер"
        @click="markerModalOpen = true"
      >
        <span class="order-marker-picker__plus" aria-hidden="true" />
      </button>
    </div>

    <MarkerAddModal v-model="markerModalOpen" @add="onMarkerAdd" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import MarkerAddModal from '@/components/crm/MarkerAddModal.vue'
import { ORDER_MARKER_OPTIONS } from '@/constants/crm.js'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  readonly: {
    type: Boolean,
    default: false
  },
  /** При открытии формы сбрасывает локальный список маркеров к дефолту */
  active: {
    type: Boolean,
    default: true
  },
  /** На белой модалке — тёмно-синий плюс, на тёмной панели — белый */
  light: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

function cloneDefaultMarkers() {
  return ORDER_MARKER_OPTIONS.map(item => ({ ...item }))
}

const markers = ref(cloneDefaultMarkers())
const markerModalOpen = ref(false)

watch(
  () => props.active,
  open => {
    if (!open) return
    markers.value = cloneDefaultMarkers()
    markerModalOpen.value = false
  }
)

function selectMarker(id) {
  if (props.readonly) return
  emit('update:modelValue', props.modelValue === id ? '' : id)
}

function onMarkerAdd({ name, color }) {
  const marker = {
    id: `marker-${Date.now()}`,
    name,
    color
  }
  markers.value.push(marker)
  emit('update:modelValue', marker.id)
}
</script>

<style scoped lang="scss">
.order-marker-picker-wrap {
  width: 100%;
  min-width: 0;
}

.order-marker-picker {
  display: flex;
  align-items: flex-start;
  gap: 0;
  width: 100%;
  min-width: 0;
}

.order-marker-picker__list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  flex: 1;
  min-width: 0;
}

.order-marker-picker__add {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  border: none;
  background: transparent;
  cursor: pointer;
  line-height: 0;

  &:hover {
    opacity: 0.85;
  }

  &:focus-visible {
    outline: 2px solid #093095;
    outline-offset: 2px;
  }
}

.order-marker-picker__plus {
  display: block;
  width: 14px;
  height: 14px;
  background-color: #fff;
  mask-image: url('/admin/icons/crm/plus.svg');
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
  -webkit-mask-image: url('/admin/icons/crm/plus.svg');
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  -webkit-mask-size: contain;
}

.order-marker-picker-wrap--light .order-marker-picker__plus {
  background-color: #182e5a;
}

.order-marker-chip {
  display: inline-flex;
  align-items: center;
  padding: 0;
  border: none;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  outline: none;

  &:disabled {
    cursor: default;
  }

  &:focus-visible {
    outline: 2px solid #093095;
    outline-offset: 1px;
  }
}

.order-marker-chip--selected {
  background: #d1daf3;
  outline: 1px solid #093095;

  .order-marker-chip__name {
    color: #093095;
  }
}

.order-marker-chip__dot {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #fff;
  box-sizing: border-box;
}

.order-marker-chip__name {
  padding: 5px 10px 5px 5px;
  font-weight: 400;
  font-size: 8px;
  line-height: 10px;
  color: #7a82a0;
  white-space: nowrap;
}
</style>
