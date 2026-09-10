<template>
  <BaseFormBlock
    :class="['order-client-fields', blockClass]"
    title="Информация о клиенте"
    layout="horizontal"
  >
    <BaseField
      v-model="draft.clientName"
      layout="horizontal"
      label="ФИО"
      placeholder="Фамилия Имя Отчество"
      :readonly="readonly"
      :required="required && !readonly"
      required-message="Напишите ФИО клиента"
      block
    />
    <BaseField
      v-model="draft.phone"
      layout="horizontal"
      label="Номер"
      placeholder="+7 000 000-00-00"
      mask="+7 ### ###-##-##"
      :readonly="readonly"
      :validate="required && !readonly ? phoneRule : null"
      block
    />
    <BaseField
      v-model="draft.email"
      layout="horizontal"
      label="Почта"
      placeholder="Электронная почта"
      :readonly="readonly"
      block
    />
    <BaseField
      v-model="draft.description"
      class="order-client-fields__textarea"
      layout="horizontal"
      type="textarea"
      label="Описание"
      placeholder="Описание"
      :readonly="readonly"
      block
    />
    <div v-if="!hideAppointment" class="order-client-fields__h-field">
      <span class="order-client-fields__label">Запись</span>
      <div class="order-client-fields__pair">
        <BaseInput
          v-model="draft.date"
          mask="##.##.####"
          placeholder="Дата"
          :readonly="readonly"
          block
        />
        <BaseInput
          v-model="draft.time"
          mask="##:##"
          placeholder="Время"
          :readonly="readonly"
          block
        />
      </div>
    </div>
    <div class="order-client-fields__h-field">
      <span class="order-client-fields__label">Источник</span>
      <BaseSelect
        v-model="draft.source"
        :options="sourceOptions"
        placeholder="Выберите источник"
        block
        :disable="readonly"
        :hide-chevron="readonly"
        :required="required && !readonly"
        required-message="Выберите вид источника"
      />
    </div>
    <div class="order-client-fields__h-field order-client-fields__h-field--markers">
      <span class="order-client-fields__label">Маркер</span>
      <div class="order-client-fields__markers">
        <div class="order-client-fields__markers-list" role="listbox" aria-label="Маркеры">
          <button
            v-for="marker in markers"
            :key="marker.id"
            type="button"
            class="order-marker-chip"
            :class="{ 'order-marker-chip--selected': draft.markerId === marker.id }"
            role="option"
            :aria-selected="draft.markerId === marker.id"
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
        <div v-if="!readonly" class="order-client-fields__markers-add">
          <button
            type="button"
            class="order-client-fields__markers-add-btn"
            aria-label="Добавить маркер"
            @click="markerModalOpen = true"
          >
            <img src="/admin/icons/crm/plus.svg" alt="" width="14" height="14" />
          </button>
        </div>
      </div>
    </div>
  </BaseFormBlock>

  <MarkerAddModal v-model="markerModalOpen" @add="onMarkerAdd" />
</template>

<script setup>
import { ref } from 'vue'
import MarkerAddModal from '@/components/crm/MarkerAddModal.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import { requiredPhone } from '@/composables/useFormValidation.js'
import { ORDER_MARKER_OPTIONS } from '@/constants/crm.js'

const props = defineProps({
  draft: {
    type: Object,
    required: true
  },
  sourceOptions: {
    type: Array,
    default: () => []
  },
  readonly: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  blockClass: {
    type: String,
    default: ''
  },
  hideAppointment: {
    type: Boolean,
    default: false
  }
})

const phoneRule = requiredPhone('Введите номер телефона клиента')
const markers = ref(ORDER_MARKER_OPTIONS.map(item => ({ ...item })))
const markerModalOpen = ref(false)

function selectMarker(id) {
  if (props.readonly) return
  props.draft.markerId = props.draft.markerId === id ? '' : id
}

function onMarkerAdd({ name, color }) {
  const marker = {
    id: `marker-${Date.now()}`,
    name,
    color
  }
  markers.value.push(marker)
  props.draft.markerId = marker.id
}
</script>

<style scoped lang="scss">
.order-client-fields {
  max-width: 400px;
}

.order-client-fields :deep(.base-field__label),
.order-client-fields__label {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.order-client-fields__h-field {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  column-gap: 15px;
  width: 100%;
}

.order-client-fields__h-field--markers {
  align-items: start;
}

.order-client-fields__label {
  grid-column: 1;
  white-space: nowrap;
}

.order-client-fields__h-field > :not(.order-client-fields__label) {
  grid-column: 2;
  min-width: 0;
  width: 100%;
}

.order-client-fields__pair {
  display: flex;
  align-items: stretch;
  gap: 10px;
  width: 100%;
}

.order-client-fields__pair > * {
  flex: 1;
  min-width: 0;
}

.order-client-fields__markers {
  display: flex;
  align-items: flex-start;
  gap: 0;
  width: 100%;
  min-width: 0;
}

.order-client-fields__markers-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px;
  flex: 1;
  min-width: 0;
}

.order-client-fields__markers-add {
  flex-shrink: 0;
}

.order-client-fields__markers-add-btn {
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

.order-client-fields__textarea {
  :deep(textarea.q-field__native) {
    max-height: calc(16px * 6);
    overflow-y: auto !important;
    resize: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      width: 0;
      height: 0;
      display: none;
    }
  }
}
</style>
