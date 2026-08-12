<template>
  <BaseModal
    :model-value="modelValue"
    size="panel"
    :title="modalTitle"
    title-uppercase
    persistent
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template v-if="isView" #title-after>
      <BaseChoice
        :model-value="null"
        :options="readonlyStatusOptions"
        shape="pill"
        variant="glass"
        :block="false"
        :disable="true"
        gap="10px"
      />
    </template>
    <template v-else #before>
      <BaseChoice
        v-model="draft.status"
        :options="statusOptions"
        shape="pill"
        variant="glass"
        :block="false"
        gap="10px"
      />
    </template>

    <div class="order-form" :class="{ 'order-form--readonly': isView }">
      <div
        class="order-form__col order-form__col--main"
        :class="{ 'order-form__col--view': isView }"
      >
        <BaseScrollbar
          v-if="isView"
          ref="viewScrollbarRef"
          track-position="start"
          class="order-form__view-body"
          content-class="order-form__view-scroll"
        >
          <OrderClientFields :draft="draft" :source-options="sourceOptions" readonly />
          <OrderCarFields :draft="draft" readonly />
        </BaseScrollbar>

        <template v-else>
          <OrderClientFields
            :draft="draft"
            :source-options="sourceOptions"
            block-class="order-form__block--client"
          />

          <BaseFormBlock title="Детали заказа" stack-fields>
            <div class="order-form__lines">
              <div class="order-form__line">
                <div class="order-form__line-service">
                  <BaseSelect
                    v-model="lineDraft.serviceId"
                    :options="serviceOptions"
                    placeholder="Виды услуг"
                    block
                  />
                </div>
                <div class="order-form__line-price">
                  <BaseInput v-model="lineDraft.price" placeholder="Цена" block />
                </div>
                <div class="order-form__line-discount">
                  <BaseInput v-model="lineDraft.discount" placeholder="Скидка" block />
                </div>
                <div class="order-form__line-master">
                  <BaseSelect
                    v-model="lineDraft.masterId"
                    :options="masterOptions"
                    placeholder="Мастер"
                    block
                  />
                </div>
                <BaseButton color="blue2" size="sm" class="order-form__line-btn" @click="addLine">
                  Добавить
                </BaseButton>
              </div>

              <div v-if="draft.lines.length" class="order-lines">
                <div class="order-lines__head">
                  <div class="order-lines__head-cols">
                    <span class="order-lines__th">№</span>
                    <span class="order-lines__th">Услуга</span>
                    <span class="order-lines__th">Сумма</span>
                    <span class="order-lines__th">Мастер</span>
                    <span class="order-lines__th">Скидка</span>
                    <span class="order-lines__th">Итого</span>
                  </div>
                  <span class="order-lines__th-spacer" aria-hidden="true" />
                </div>

                <div class="order-lines__body">
                  <div v-for="(line, index) in draft.lines" :key="index" class="order-lines__row">
                    <div class="order-lines__cells">
                      <div class="order-lines__cell order-lines__cell--num">
                        {{ formatLineIndex(index) }}
                      </div>
                      <div class="order-lines__cell order-lines__cell--service">
                        {{ lineServiceLabel(line) }}
                      </div>
                      <div class="order-lines__cell order-lines__cell--sum">
                        <span>{{ formatLineMoney(line.price) }}</span>
                        <span class="order-lines__unit">₽</span>
                      </div>
                      <div class="order-lines__cell order-lines__cell--master">
                        {{ lineMasterLabel(line) }}
                      </div>
                      <div class="order-lines__cell order-lines__cell--discount">
                        <span>{{ line.discount || '0' }}</span>
                        <span class="order-lines__unit">%</span>
                      </div>
                      <div class="order-lines__cell order-lines__cell--total">
                        <span class="order-lines__total-value">{{ formatLineTotal(line) }}</span>
                        <span class="order-lines__unit">₽</span>
                      </div>
                    </div>
                    <BaseButton
                      color="red"
                      size="sm"
                      class="order-lines__remove"
                      @click="removeLine(index)"
                    >
                      Удалить
                    </BaseButton>
                  </div>
                </div>
              </div>
            </div>
          </BaseFormBlock>
        </template>
      </div>

      <div
        class="order-form__col"
        :class="isView ? 'order-form__col--side' : 'order-form__col--car'"
      >
        <div v-if="isView" class="order-docs">
          <h2 class="order-docs__title">Документы клиента</h2>

          <div v-if="!isDoneStatus" class="order-docs__placeholder order-docs__glass">
            Здесь будут документы клиента
          </div>

          <template v-else-if="viewDocuments.length">
            <div class="order-docs__list">
              <div
                v-for="doc in viewDocuments"
                :key="doc.id"
                class="order-docs__card order-docs__glass"
              >
                <div class="order-docs__card-main">
                  <PdfIcon :size="56" :color="doc.color" class="order-docs__pdf" />
                  <div class="order-docs__info">
                    <p class="order-docs__name">{{ doc.title }}</p>
                    <p class="order-docs__meta">{{ doc.meta }}</p>
                    <p class="order-docs__date">{{ doc.date }}</p>
                  </div>
                </div>
                <div class="order-docs__card-actions">
                  <button type="button" class="order-docs__icon-btn" aria-label="Скачать">
                    <img src="/admin/icons/crm/docs/download.svg" alt="" width="18" height="19" />
                  </button>
                  <button type="button" class="order-docs__icon-btn" aria-label="Печать">
                    <PrinterIcon :size="22" />
                  </button>
                </div>
              </div>
            </div>

            <div class="order-docs__footer">
              <button type="button" class="order-docs__action order-docs__glass">
                <PrinterIcon :size="22" />
                <span>Напечатать все</span>
              </button>
              <button type="button" class="order-docs__action order-docs__glass">
                <img src="/admin/icons/crm/docs/archive.svg" alt="" width="18" height="18" />
                <span>Скачать пакетом</span>
              </button>
            </div>
          </template>

          <template v-else>
            <button type="button" class="order-docs__upload order-docs__glass">
              Загрузить документы
            </button>

            <div class="order-docs__divider">
              <span class="order-docs__divider-line" />
              <span class="order-docs__divider-text">или</span>
              <span class="order-docs__divider-line" />
            </div>

            <button type="button" class="order-docs__generate order-docs__glass">
              Сгенерировать документы
            </button>
          </template>
        </div>

        <OrderCarFields v-else :draft="draft" />

        <div class="order-form__actions">
          <template v-if="isView">
            <BaseButton color="red" size="lg" @click="emit('delete', props.order)">
              Удалить заказ
            </BaseButton>
            <BaseButton color="blue2" size="lg" @click="emit('edit')">
              Редактировать заказ
            </BaseButton>
          </template>
          <template v-else>
            <BaseButton color="red" size="lg" @click="emit('update:modelValue', false)">
              Отмена
            </BaseButton>
            <BaseButton color="green" size="lg" :loading="saving" @click="onSave">
              {{ isEdit ? 'Сохранить изменения' : 'Создать заказ' }}
            </BaseButton>
          </template>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import OrderCarFields from '@/components/crm/OrderCarFields.vue'
import OrderClientFields from '@/components/crm/OrderClientFields.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseScrollbar from '@/components/ui/BaseScrollbar.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import PdfIcon from '@/components/ui/PdfIcon.vue'
import PrinterIcon from '@/components/ui/PrinterIcon.vue'
import { crmApi } from '@/api/index.js'
import {
  CRM_STATUS_LIST,
  ORDER_SOURCE_OPTIONS,
  formatCrmMoney,
  formatCrmOrderNumber
} from '@/constants/crm.js'
import { formatSurnameInitial } from '@/utils/name.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'create',
    validator: value => ['create', 'edit', 'view'].includes(value)
  },
  order: {
    type: Object,
    default: null
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

const emit = defineEmits(['update:modelValue', 'save', 'edit', 'delete'])

const draft = reactive(createEmptyDraft())
const lineDraft = reactive(emptyLine())
const serviceOptions = ref([])
const masterOptions = ref([])

const viewScrollbarRef = ref(null)

const isView = computed(() => props.mode === 'view')
const isEdit = computed(() => props.mode === 'edit')
const isDoneStatus = computed(() => draft.status === 'done')

const viewDocuments = computed(() =>
  Array.isArray(props.order?.documents) ? props.order.documents : []
)

const modalTitle = computed(() =>
  formatCrmOrderNumber(props.order?.number || props.orderNumber || 0)
)

const statusOptions = computed(() =>
  CRM_STATUS_LIST.map(({ value, label, color, bg }) => ({
    value,
    label,
    activeColor: color,
    activeBg: bg
  }))
)

const readonlyStatusOptions = computed(() => {
  const current = CRM_STATUS_LIST.find(item => item.value === draft.status) || CRM_STATUS_LIST[0]
  return [
    {
      value: current.value,
      label: current.label
    }
  ]
})

const sourceOptions = ORDER_SOURCE_OPTIONS

watch(
  () => [props.modelValue, props.mode, props.order],
  async ([open]) => {
    if (!open) return

    if (props.mode === 'create') {
      Object.assign(draft, createEmptyDraft())
    } else if (props.order) {
      Object.assign(draft, draftFromOrder(props.order))
    }
    Object.assign(lineDraft, emptyLine())

    if (props.mode !== 'view' && !serviceOptions.value.length) {
      const [services, employees] = await Promise.all([crmApi.services(), crmApi.employees()])
      serviceOptions.value = (services || []).map(item => ({
        value: item.id,
        label: item.title,
        price: item.price == null ? null : Number(item.price)
      }))
      masterOptions.value = (employees || []).map(item => ({
        value: item.id,
        label: item.name
      }))
    }

    await nextTick()
    viewScrollbarRef.value?.update()
  }
)

watch(
  () => lineDraft.serviceId,
  serviceId => {
    const selected = serviceOptions.value.find(item => item.value === serviceId)
    lineDraft.price = selected?.price == null ? '' : String(selected.price)
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
    lines: [],
    plate: '',
    brand: '',
    model: '',
    year: '',
    color: '',
    vin: '',
    mileage: ''
  }
}

function splitCarBrand(carBrand) {
  const parts = String(carBrand || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
  return {
    brand: parts[0] || '',
    model: parts.slice(1).join(' ')
  }
}

function draftFromOrder(order) {
  const fromBrand = splitCarBrand(order.carBrand)
  return {
    ...createEmptyDraft(),
    status: order.status || 'new',
    clientName: order.clientName || '',
    phone: order.phone || '',
    email: order.email || '',
    description: order.description || '',
    date: order.date || '',
    time: order.time || '',
    source: order.source || '',
    lines:
      Array.isArray(order.lines) && order.lines.length
        ? order.lines.map(line => ({
            serviceId: line.serviceId || '',
            price: line.price != null ? String(line.price) : '',
            discount: line.discount != null ? String(line.discount) : '',
            masterId: line.masterId || ''
          }))
        : [],
    plate: order.plate || '',
    brand: order.brand || fromBrand.brand,
    model: order.model || fromBrand.model,
    year:
      order.year != null && order.year !== ''
        ? String(order.year)
        : order.carYear != null
          ? String(order.carYear)
          : '',
    color: order.color || '',
    vin: order.vin || '',
    mileage: order.mileage != null && order.mileage !== '' ? String(order.mileage) : ''
  }
}

function addLine() {
  if (!lineDraft.serviceId && lineDraft.price === '' && !lineDraft.masterId) return
  draft.lines.push({
    serviceId: lineDraft.serviceId,
    price: lineDraft.price,
    discount: lineDraft.discount,
    masterId: lineDraft.masterId
  })
  Object.assign(lineDraft, emptyLine())
}

function removeLine(index) {
  draft.lines.splice(index, 1)
}

function formatLineIndex(index) {
  return String(index + 1).padStart(2, '0')
}

function optionLabel(options, value, fallback = '—') {
  return options.find(item => item.value === value)?.label || fallback
}

function lineServiceLabel(line) {
  return optionLabel(serviceOptions.value, line.serviceId)
}

function lineMasterLabel(line) {
  return formatSurnameInitial(optionLabel(masterOptions.value, line.masterId, '')) || '—'
}

function lineTotal(line) {
  const price = Number(line.price) || 0
  const discount = Math.min(100, Math.max(0, Number(line.discount) || 0))
  return Math.max(0, Math.round(price * (1 - discount / 100)))
}

function formatLineMoney(value) {
  return formatCrmMoney(Number(value) || 0)
}

function formatLineTotal(line) {
  return formatCrmMoney(lineTotal(line))
}

function onSave() {
  const lines = draft.lines.map(line => ({
    serviceId: line.serviceId,
    price: line.price === '' ? 0 : Number(line.price),
    discount: line.discount === '' ? 0 : Number(line.discount),
    masterId: line.masterId
  }))
  const services = lines
    .map(line => serviceOptions.value.find(item => item.value === line.serviceId)?.label)
    .filter(Boolean)
  const masterNames = lines
    .map(line => masterOptions.value.find(item => item.value === line.masterId)?.label)
    .filter(Boolean)
  const amount = lines.reduce((sum, line) => sum + lineTotal(line), 0)

  emit('save', {
    id: props.order?.id || null,
    number: props.order?.number || 0,
    status: draft.status,
    clientName: draft.clientName.trim(),
    phone: draft.phone,
    email: draft.email.trim(),
    description: draft.description.trim(),
    date: draft.date,
    time: draft.time,
    source: draft.source,
    lines,
    amount,
    services,
    master: masterNames[0] || '',
    masters: masterNames.join(', '),
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

.order-form--readonly {
  pointer-events: none;
}

.order-form--readonly .order-form__actions,
.order-form--readonly .order-docs,
.order-form--readonly .order-form__view-body {
  pointer-events: auto;
}

.order-form--readonly .order-form__view-body :deep(.order-form__view-scroll .base-input),
.order-form--readonly .order-form__view-body :deep(.order-form__view-scroll .base-select),
.order-form--readonly .order-form__view-body :deep(.order-form__view-scroll .base-field__label),
.order-form--readonly
  .order-form__view-body
  :deep(.order-form__view-scroll .order-client-fields__label),
.order-form--readonly
  .order-form__view-body
  :deep(.order-form__view-scroll .order-car-fields__label) {
  pointer-events: none;
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

.order-form__col--view {
  overflow: hidden;
}

.order-form__view-body {
  flex: 1;
  min-height: 0;
  width: 100%;
  gap: 12px;
  --base-scrollbar-thumb: #093095;
}

.order-form__view-body :deep(.order-form__view-scroll) {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.order-form__col--car,
.order-form__col--side {
  flex: 0 1 500px;
  max-width: 500px;
  margin-left: auto;
  align-items: flex-end;
}

.order-form__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 20px;
  margin-top: auto;
  flex-shrink: 0;
  width: 100%;
}

.order-docs {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 15px;
  width: 100%;
  min-height: 0;
}

.order-docs__title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 16px;
  font-weight: 600;
  line-height: normal;
  text-transform: uppercase;
}

.order-docs__glass {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    z-index: 1;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.5) 0%,
      rgba(255, 255, 255, 0) 22%,
      rgba(255, 255, 255, 0) 78%,
      rgba(255, 255, 255, 0.4) 100%
    );
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }

  > * {
    position: relative;
    z-index: 2;
  }
}

.order-docs__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 120px;
  border-radius: 8px;
  box-sizing: border-box;
  color: var(--dvijok-white);
  font-weight: 700;
  font-size: 13px;
  line-height: 16px;
  text-align: center;
}

.order-docs__upload {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 180px;
  padding: 30px;
  border-radius: 8px;
  box-sizing: border-box;
  color: var(--dvijok-white);
  font-weight: 700;
  font-size: 13px;
  line-height: normal;
  cursor: pointer;
}

.order-docs__divider {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.order-docs__divider-line {
  flex: 1;
  height: 1px;
  background: #7a82a0;
  opacity: 0.6;
}

.order-docs__divider-text {
  color: #7a82a0;
  font-size: 12px;
  font-weight: 600;
  line-height: normal;
}

.order-docs__generate,
.order-docs__action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 15px 30px;
  border-radius: 10px;
  box-sizing: border-box;
  color: var(--dvijok-white);
  font-size: 14px;
  font-weight: 600;
  line-height: normal;
  cursor: pointer;
  white-space: nowrap;
}

.order-docs__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.order-docs__card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  box-sizing: border-box;
}

.order-docs__card-main {
  display: flex;
  align-items: center;
  gap: 30px;
  min-width: 0;
}

.order-docs__pdf {
  flex-shrink: 0;
}

.order-docs__info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.order-docs__name {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 13px;
  font-weight: 700;
  line-height: normal;
}

.order-docs__meta,
.order-docs__date {
  margin: 0;
  color: #7a82a0;
  font-size: 12px;
  line-height: normal;
}

.order-docs__meta {
  font-weight: 600;
}

.order-docs__date {
  font-weight: 400;
}

.order-docs__card-actions {
  display: flex;
  align-items: center;
  gap: 30px;
  flex-shrink: 0;
}

.order-docs__icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--dvijok-white);
  cursor: pointer;
}

.order-docs__footer {
  display: flex;
  align-items: stretch;
  gap: 20px;
  width: 100%;
}

.order-docs__footer .order-docs__action {
  flex: 1;
}

.order-form__lines {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
  max-width: 600px;
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
  flex: 1 1 0;
  min-width: 0;
}

.order-form__line-price,
.order-form__line-discount {
  flex: 0.5 1 0;
  min-width: 80px;
}

.order-form__line-btn {
  flex: 0 0 100px;
  width: 100px;
  min-width: 100px;
  box-sizing: border-box;
  justify-content: center;
}

.order-lines {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0;
  width: 100%;
}

.order-lines__head {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 35px;
}

.order-lines__head-cols {
  flex: 1 1 auto;
  min-width: 0;
  display: grid;
  grid-template-columns: 34px minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1.1fr) 64px minmax(
      0,
      1.1fr
    );
  align-items: center;
}

.order-lines__th {
  padding: 10px 10px 10px 0;
  box-sizing: border-box;
  color: #7a82a0;
  font-size: 12px;
  font-weight: 600;
  line-height: normal;
  white-space: nowrap;
}

.order-lines__th-spacer {
  flex: 0 0 100px;
  width: 100px;
}

.order-lines__body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
}

.order-lines__row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.order-lines__cells {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: 34px minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1.1fr) 64px minmax(
      0,
      1.1fr
    );
  align-items: stretch;
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  background-color: transparent;
  background-image: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.14) 0%,
    rgba(255, 255, 255, 0.05) 35%,
    rgba(255, 255, 255, 0.02) 65%,
    rgba(255, 255, 255, 0.08) 100%
  );
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.order-lines__cells::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0) 22%,
    rgba(255, 255, 255, 0) 78%,
    rgba(255, 255, 255, 0.35) 100%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
}

.order-lines__cell {
  position: relative;
  z-index: 0;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px;
  box-sizing: border-box;
  min-width: 0;
  min-height: 32px;
  color: var(--dvijok-white);
  font-size: 10px;
  font-weight: 600;
  line-height: normal;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-lines__cell + .order-lines__cell {
  box-shadow: inset 1px 0 0 rgba(255, 255, 255, 0.22);
}

.order-lines__cell--sum,
.order-lines__cell--discount,
.order-lines__cell--total {
  justify-content: space-between;
}

.order-lines__unit {
  flex-shrink: 0;
  width: 14px;
  text-align: right;
  font-size: 10px;
  font-weight: 700;
  line-height: normal;
  color: var(--dvijok-white);
}

.order-lines__total-value {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-lines__remove {
  flex: 0 0 100px;
  width: 100px;
  min-width: 100px;
  box-sizing: border-box;
  justify-content: center;
}
</style>
