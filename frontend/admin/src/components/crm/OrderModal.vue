<template>
  <BaseModal
    :model-value="modelValue"
    size="panel"
    :title="modalTitle"
    title-uppercase
    persistent
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #before>
      <BaseChoice
        v-model="draft.status"
        :options="statusOptions"
        shape="pill"
        variant="glass"
        :block="false"
        gap="10px"
      />
    </template>

    <div class="order-form">
      <div class="order-form__col order-form__col--main">
        <BaseFormBlock
          class="order-form__block order-form__block--client"
          title="Информация о клиенте"
          layout="horizontal"
        >
          <BaseField
            v-model="draft.clientName"
            layout="horizontal"
            label="ФИО"
            placeholder="Фамилия Имя Отчество"
            block
          />
          <BaseField
            v-model="draft.phone"
            layout="horizontal"
            label="Номер"
            placeholder="+7 000 000-00-00"
            mask="+7 ### ###-##-##"
            block
          />
          <BaseField
            v-model="draft.email"
            layout="horizontal"
            label="Почта"
            placeholder="Электронная почта"
            block
          />
          <BaseField
            v-model="draft.description"
            class="order-form__textarea"
            layout="horizontal"
            type="textarea"
            label="Описание"
            placeholder="Описание"
            block
          />
          <div class="order-form__h-field">
            <span class="order-form__label">Запись</span>
            <div class="order-form__pair">
              <BaseInput v-model="draft.date" mask="##.##.####" placeholder="Дата" block />
              <BaseInput v-model="draft.time" mask="##:##" placeholder="Время" block />
            </div>
          </div>
          <div class="order-form__h-field">
            <span class="order-form__label">Источник</span>
            <BaseSelect
              v-model="draft.source"
              :options="sourceOptions"
              placeholder="Выберите источник"
              block
            />
          </div>
        </BaseFormBlock>

        <BaseFormBlock title="Детали заказа" stack-fields>
          <div class="order-form__lines">
            <div v-for="(line, index) in draft.lines" :key="index" class="order-form__line">
              <div class="order-form__line-service">
                <BaseSelect
                  v-model="line.serviceId"
                  :options="serviceOptions"
                  placeholder="Виды услуг"
                  block
                />
              </div>
              <div class="order-form__line-price">
                <BaseInput v-model="line.price" placeholder="Цена" block />
              </div>
              <div class="order-form__line-discount">
                <BaseInput v-model="line.discount" placeholder="Скидка" block />
              </div>
              <div class="order-form__line-master">
                <BaseSelect
                  v-model="line.masterId"
                  :options="masterOptions"
                  placeholder="Мастер"
                  block
                />
              </div>
              <BaseButton
                v-if="index === 0"
                color="blue2"
                size="sm"
                class="order-form__line-btn"
                @click="addLine"
              >
                Добавить
              </BaseButton>
              <BaseButton
                v-else
                color="red"
                size="sm"
                class="order-form__line-btn"
                @click="removeLine(index)"
              >
                Удалить
              </BaseButton>
            </div>
          </div>
        </BaseFormBlock>
      </div>

      <div class="order-form__col order-form__col--car">
        <BaseFormBlock title="Автомобиль" layout="horizontal">
          <BaseField
            v-model="draft.plate"
            layout="horizontal"
            label="Гос. номер"
            placeholder="Гос. номер"
            block
          />
          <BaseField
            v-model="draft.brand"
            layout="horizontal"
            label="Марка"
            placeholder="Марка"
            block
          />
          <BaseField
            v-model="draft.model"
            layout="horizontal"
            label="Модель"
            placeholder="Модель"
            block
          />
          <div class="order-form__h-field">
            <span class="order-form__label">Год/цвет</span>
            <div class="order-form__pair">
              <BaseInput v-model="draft.year" placeholder="Год" block />
              <BaseInput v-model="draft.color" placeholder="Цвет" block />
            </div>
          </div>
          <BaseField
            v-model="draft.vin"
            layout="horizontal"
            label="VIN"
            placeholder="17 символов из ПТС"
            mask="NNNNNNNNNNNNNNNNN"
            block
          />
          <BaseField
            v-model="draft.mileage"
            layout="horizontal"
            type="number"
            label="Пробег"
            placeholder="Пробег в км"
            block
          />
        </BaseFormBlock>
      </div>
    </div>

    <template #actions>
      <BaseButton color="red" size="lg" @click="emit('update:modelValue', false)">
        Отмена
      </BaseButton>
      <BaseButton color="green" size="lg" :loading="saving" @click="onSave">
        Создать заказ
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import { servicesApi, tasksApi } from '@/api/index.js'
import { CRM_STATUS_LIST, ORDER_SOURCE_OPTIONS, formatCrmOrderNumber } from '@/constants/crm.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  orderNumber: {
    type: Number,
    default: 0
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const draft = reactive(createEmptyDraft())
const serviceOptions = ref([])
const masterOptions = ref([])

const modalTitle = computed(() => formatCrmOrderNumber(props.orderNumber))

const statusOptions = computed(() =>
  CRM_STATUS_LIST.map(({ value, label, color, bg }) => ({
    value,
    label,
    activeColor: color,
    activeBg: bg
  }))
)

const sourceOptions = ORDER_SOURCE_OPTIONS

watch(
  () => props.modelValue,
  async open => {
    if (!open) return
    Object.assign(draft, createEmptyDraft())
    const [services, employees] = await Promise.all([servicesApi.list(), tasksApi.employees()])
    serviceOptions.value = (services || []).map(item => ({
      value: item.id,
      label: item.title
    }))
    masterOptions.value = (employees || []).map(item => ({
      value: item.id,
      label: item.name
    }))
  }
)

function emptyLine() {
  return {
    serviceId: '',
    price: '',
    discount: '',
    masterId: ''
  }
}

function createEmptyDraft() {
  return {
    status: 'new',
    clientName: '',
    phone: '',
    email: '',
    description: '',
    date: '',
    time: '',
    source: '',
    lines: [emptyLine()],
    plate: '',
    brand: '',
    model: '',
    year: '',
    color: '',
    vin: '',
    mileage: ''
  }
}

function addLine() {
  draft.lines.push(emptyLine())
}

function removeLine(index) {
  if (index === 0) return
  draft.lines.splice(index, 1)
}

function onSave() {
  emit('save', {
    status: draft.status,
    clientName: draft.clientName.trim(),
    phone: draft.phone,
    email: draft.email.trim(),
    description: draft.description.trim(),
    date: draft.date,
    time: draft.time,
    source: draft.source,
    lines: draft.lines.map(line => ({
      serviceId: line.serviceId,
      price: line.price === '' ? 0 : Number(line.price),
      discount: line.discount === '' ? 0 : Number(line.discount),
      masterId: line.masterId
    })),
    plate: draft.plate.trim(),
    brand: draft.brand.trim(),
    model: draft.model.trim(),
    year: draft.year.trim(),
    color: draft.color.trim(),
    vin: draft.vin.trim(),
    mileage: draft.mileage === '' ? null : Number(draft.mileage)
  })
}
</script>

<style scoped lang="scss">
.order-form {
  --dvijok-form-block-title: var(--dvijok-white);
  --dvijok-form-label: var(--dvijok-text-secondary);

  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: space-between;
  gap: 50px;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.order-form__col {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 30px;
  overflow: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.order-form__col--main {
  flex: 1 1 auto;
}

.order-form__col--car {
  flex: 0 1 400px;
  max-width: 400px;
  margin-left: auto;
}

.order-form__block--client {
  max-width: 400px;
}

.order-form :deep(.base-field__label),
.order-form__label {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.order-form__h-field {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  column-gap: 15px;
  width: 100%;
}

.order-form__label {
  grid-column: 1;
  white-space: nowrap;
}

.order-form__h-field > :not(.order-form__label) {
  grid-column: 2;
  min-width: 0;
  width: 100%;
}

.order-form__pair {
  display: flex;
  align-items: stretch;
  gap: 10px;
  width: 100%;
}

.order-form__pair > * {
  flex: 1;
  min-width: 0;
}

.order-form__textarea {
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

.order-form__lines {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.order-form__line {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.order-form__line-service,
.order-form__line-master {
  flex: 0 0 200px;
  width: 200px;
}

.order-form__line-price,
.order-form__line-discount {
  flex: 0 0 100px;
  width: 100px;
}

.order-form__line-btn {
  flex: 0 0 100px;
  width: 100px;
  min-width: 100px;
  box-sizing: border-box;
  justify-content: center;
}
</style>
