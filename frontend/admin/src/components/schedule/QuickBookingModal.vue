<template>
  <BaseModal
    :model-value="modelValue"
    fit
    padding="20px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="quick-booking">
      <BaseFormBlock title="Быстрая запись">
        <BaseField
          v-model="draft.clientName"
          label="ФИО"
          placeholder="Фамилия Имя Отчество"
          required
          required-message="Напишите ФИО клиента"
          block
        />
        <BaseField
          v-model="draft.phone"
          label="Номер телефона"
          placeholder="+7 000 000-00-00"
          mask="+7 ### ###-##-##"
          :validate="phoneRule"
          block
        />
        <BaseField
          v-model="draft.description"
          type="textarea"
          label="Описание"
          placeholder="Описание"
          block
        />

        <div class="quick-booking__info">
          <span class="quick-booking__info-label">Детали записи</span>
          <div class="quick-booking__info-body">
            <p class="quick-booking__info-line">{{ detailsDateTime }}</p>
            <p class="quick-booking__info-line">Мастер: {{ detailsMaster }}</p>
          </div>
        </div>

        <div class="quick-booking__markers">
          <span class="quick-booking__markers-label">Маркер</span>
          <OrderMarkerPicker v-model="draft.markerId" :active="modelValue" />
        </div>
      </BaseFormBlock>

      <div class="quick-booking__actions">
        <BaseButton text :underline="false" color="blue1" :loading="saving" @click="onAdd">
          Добавить
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import OrderMarkerPicker from '@/components/crm/OrderMarkerPicker.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { createFormValidation, requiredPhone } from '@/composables/useFormValidation.js'
import { formatRuDayMonth } from '@/utils/formatDateRu.js'
import { getShortName } from '@/utils/name.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  appointment: {
    type: Object,
    default: null
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'add'])

const form = createFormValidation()
const phoneRule = requiredPhone('Введите номер телефона клиента')

function emptyDraft() {
  return {
    clientName: '',
    phone: '',
    description: '',
    markerId: ''
  }
}

const draft = reactive(emptyDraft())

const detailsDateTime = computed(() => {
  if (!props.appointment?.date || !props.appointment?.time) return ''
  return `${formatRuDayMonth(props.appointment.date)}, ${props.appointment.time}`
})

const detailsMaster = computed(() => getShortName(props.appointment?.employeeName || ''))

watch(
  () => props.modelValue,
  open => {
    if (!open) return
    Object.assign(draft, emptyDraft())
    form.reset()
  }
)

function onAdd() {
  if (!form.validate()) return
  emit('add', {
    clientName: draft.clientName,
    phone: draft.phone,
    description: draft.description,
    markerId: draft.markerId,
    date: props.appointment?.date || '',
    time: props.appointment?.time || '',
    employeeId: props.appointment?.employeeId ?? '',
    employeeName: props.appointment?.employeeName || ''
  })
}
</script>

<style scoped lang="scss">
.quick-booking {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  padding-right: 24px;
  box-sizing: border-box;
}

.quick-booking__info,
.quick-booking__markers {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  max-width: 325px;
}

.quick-booking__info-label,
.quick-booking__markers-label {
  color: var(--dvijok-form-label, var(--dvijok-bg-dark));
  font-size: 16px;
  line-height: 19px;
  text-align: left;
  white-space: nowrap;
}

.quick-booking__info-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
}

.quick-booking__info-line {
  margin: 0;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: #7a82a0;
}

.quick-booking__actions {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
</style>
