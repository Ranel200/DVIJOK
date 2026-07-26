<template>
  <div class="settings">
    <div class="settings__col">
      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Данные автосервиса</h2>
          <button
            type="button"
            class="settings-card__edit"
            aria-label="Редактировать"
            @click="openEdit()"
          >
            <img src="/admin/icons/services/edit.svg" alt="" />
          </button>
        </div>
        <BaseForm v-model="form" :blocks="formBlocks" disable max-height="none" />
      </section>
    </div>

    <div class="settings__col">
      <section class="settings-card settings-card--subscription">
        <h2 class="settings-card__title settings-card__title--light">Статус подписки</h2>

        <div class="subscription__status-row">
          <div
            class="subscription__pill"
            :style="{
              background: statusMeta.bg,
              color: statusMeta.color,
              borderColor: statusMeta.color
            }"
          >
            <Radio filled :color="statusMeta.color" :size="20" />
            <span>{{ statusMeta.label }}</span>
          </div>

          <div class="subscription__meta">
            <span class="subscription__meta-label">Активен до</span>
            <span class="subscription__meta-value">{{ activeUntilLabel }}</span>
            <span class="subscription__meta-label">
              {{ daysLeftLabel }} · {{ subscription.plan }}
            </span>
          </div>
        </div>

        <div class="subscription__usage">
          <span class="subscription__meta-label">
            Использовано {{ subscription.usedMonths }} из {{ subscription.totalMonths }} мес.
          </span>
          <div class="subscription__progress">
            <div class="subscription__progress-fill" :style="{ width: progressWidth }" />
          </div>
        </div>

        <div class="subscription__features">
          <div
            v-for="(column, colIndex) in featureColumns"
            :key="colIndex"
            class="subscription__features-col"
          >
            <div v-for="feature in column" :key="feature.label" class="subscription__feature">
              <div class="subscription__feature-icon">
                <img :src="`/admin/icons/settings/${feature.icon}.svg`" alt="" />
              </div>
              <span class="subscription__meta-label">{{ feature.label }}</span>
            </div>
          </div>
        </div>

        <BaseButton
          color="blue1"
          scheme="outlinedWhite-solid-light"
          size="lg"
          block
          :icon-spacing="10"
          class="subscription__change"
        >
          Изменить тариф
          <template #append>
            <ArrowIcon direction="right" />
          </template>
        </BaseButton>
      </section>

      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Логотип и описание</h2>
          <button
            type="button"
            class="settings-card__edit"
            aria-label="Редактировать"
            @click="openBrandingEdit"
          >
            <img src="/admin/icons/services/edit.svg" alt="" />
          </button>
        </div>
        <div class="branding">
          <div class="branding__logo-block">
            <span class="branding__label">Ваш логотип</span>
            <div class="branding__logo" aria-hidden="true">
              <img v-if="form.logo" :src="form.logo" alt="" />
            </div>
          </div>
          <div class="branding__desc-block">
            <span class="branding__label">Описание автосервиса</span>
            <div class="branding__desc">{{ form.description }}</div>
          </div>
        </div>
      </section>
    </div>

    <BaseModal v-model="editOpen" fit hide-close @show="onEditShow">
      <div class="service-edit">
        <h2 class="service-edit__title">Изменение данных автосервиса</h2>
        <div class="service-edit__scroll">
          <BaseForm ref="editFormRef" v-model="draft" :blocks="editBlocks" max-height="none" />
        </div>
      </div>
      <template #actions>
        <div class="service-edit__actions">
          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-outlinedWhite"
            size="lg"
            @click="editOpen = false"
          >
            Отмена
          </BaseButton>
          <BaseButton color="green" size="lg" :loading="saving" @click="saveEdit">
            Сохранить изменения
          </BaseButton>
        </div>
      </template>
    </BaseModal>

    <BaseModal v-model="brandingEditOpen" fit hide-close>
      <div class="branding-edit">
        <h2 class="branding-edit__title">Изменение логотипа и описания</h2>
        <div class="branding-edit__body">
          <div class="branding-edit__logos">
            <div class="branding-edit__col">
              <span class="branding-edit__label">Ваш логотип</span>
              <label class="branding-edit__drop">
                <input
                  type="file"
                  accept="image/*"
                  class="branding-edit__file"
                  @change="onLogoPick"
                />
                <img
                  v-if="brandingDraft.logo"
                  :src="brandingDraft.logo"
                  alt=""
                  class="branding-edit__drop-img"
                />
                <span v-else>Поместите сюда ваш логотип</span>
              </label>
            </div>
            <div class="branding-edit__col">
              <span class="branding-edit__label">Предыдущий логотип</span>
              <div class="branding-edit__prev">
                <img v-if="form.logo" :src="form.logo" alt="" />
              </div>
            </div>
          </div>

          <div class="branding-edit__desc-block">
            <span class="branding-edit__label">Описание автосервиса</span>
            <textarea
              v-model="brandingDraft.description"
              class="branding-edit__desc"
              rows="4"
              placeholder="Введите описание"
            />
          </div>
        </div>
      </div>
      <template #actions>
        <div class="branding-edit__actions">
          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-outlinedWhite"
            size="lg"
            @click="brandingEditOpen = false"
          >
            Отмена
          </BaseButton>
          <BaseButton color="green" size="lg" :loading="brandingSaving" @click="saveBranding">
            Сохранить изменения
          </BaseButton>
        </div>
      </template>
    </BaseModal>

    <BaseModal v-model="savedOpen">
      <div class="service-saved">
        <h2 class="service-saved__title">Изменения сохранены!</h2>
        <BaseButton color="blue1" size="lg" @click="savedOpen = false">Ок</BaseButton>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseForm from '@/components/ui/BaseForm.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import Radio from '@/components/ui/Radio.vue'
import { settingsApi } from '@/api/index.js'
import { formatRuDate } from '@/utils/formatDateRu.js'
import { pluralize } from '@/utils/pluralize.js'

const form = defineModel('form', { type: Object, required: true })

const props = defineProps({
  subscription: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['saved'])
const editFormRef = ref(null)

const LEGAL_OPTIONS = [
  { label: 'ИП', value: 'ИП' },
  { label: 'ООО', value: 'ООО' },
  { label: 'ОАО', value: 'ОАО' },
  { label: 'ЗАО', value: 'ЗАО' },
  { label: 'ПАО', value: 'ПАО' }
]

const TAX_OPTIONS = [
  { label: 'УСН (упрощенная)', value: 'УСН' },
  { label: 'НДС 20%', value: 'НДС' }
]

const TAX_LABELS = {
  УСН: 'УСН (упрощенная)',
  НДС: 'НДС 20%'
}

const editOpen = ref(false)
const brandingEditOpen = ref(false)
const savedOpen = ref(false)
const saving = ref(false)
const brandingSaving = ref(false)
const pendingFocusKey = ref(null)
const draft = ref({})
const brandingDraft = ref({
  logo: '',
  description: ''
})

const STATUS_MAP = {
  active: {
    label: 'Активен',
    bg: '#D5F0E4',
    color: '#157848'
  },
  expiring: {
    label: 'Скоро истечет',
    bg: '#F0E4D5',
    color: '#F0A030'
  },
  expired: {
    label: 'Истек',
    bg: '#F0D5D5',
    color: '#B60000'
  }
}

const statusMeta = computed(() => STATUS_MAP[props.subscription.status] || STATUS_MAP.active)

const formBlocks = computed(() => [
  {
    title: '',
    fields: [
      { key: 'name', label: 'Название автосервиса' },
      { key: 'headName', label: 'ФИО руководителя' }
    ]
  },
  {
    title: '',
    fields: [
      {
        key: 'legalType',
        label: 'Тип юридического лица',
        type: 'choice',
        shape: 'pill',
        block: false,
        row: 'legal',
        options: form.value.legalType
          ? [{ label: form.value.legalType, value: form.value.legalType }]
          : []
      },
      {
        key: 'taxSystem',
        label: 'Система налогообложения',
        type: 'choice',
        shape: 'rounded',
        block: false,
        row: 'legal',
        options: form.value.taxSystem
          ? [
              {
                label: TAX_LABELS[form.value.taxSystem] || form.value.taxSystem,
                value: form.value.taxSystem
              }
            ]
          : []
      },
      { key: 'inn', label: 'ИНН', row: 'ids' },
      { key: 'ogrn', label: 'ОГРН', row: 'ids' }
    ]
  },
  {
    title: '',
    fields: [
      { key: 'phone', label: 'Номер телефона' },
      { key: 'email', label: 'Адрес электронной почты' },
      { key: 'address', label: 'Фактический адрес' }
    ]
  }
])

const editBlocks = computed(() => [
  {
    title: '',
    fields: [
      { key: 'name', label: 'Название автосервиса', placeholder: 'Введите название' },
      { key: 'headName', label: 'ФИО руководителя', placeholder: 'Введите ФИО' }
    ]
  },
  {
    title: '',
    fields: [
      {
        key: 'legalType',
        label: 'Тип юридического лица',
        type: 'choice',
        shape: 'pill',
        options: LEGAL_OPTIONS
      },
      { key: 'inn', label: 'ИНН', placeholder: 'Введите ИНН', row: 'ids' },
      {
        key: 'taxSystem',
        label: 'Система налогообложения',
        type: 'choice',
        shape: 'rounded',
        block: false,
        row: 'ids',
        options: TAX_OPTIONS
      },
      { key: 'ogrn', label: 'ОГРН', placeholder: 'Введите ОГРН', row: 'ogrn' },
      { key: 'ogrnSpacer', type: 'empty', row: 'ogrn' }
    ]
  },
  {
    title: '',
    fields: [
      { key: 'phone', label: 'Номер телефона', placeholder: '+7 999 999 99 99' },
      { key: 'email', label: 'Адрес электронной почты', placeholder: 'Введите почту' },
      { key: 'address', label: 'Фактический адрес', placeholder: 'Введите адрес' }
    ]
  }
])

const activeUntilLabel = computed(() => formatRuDate(props.subscription.activeUntil))

const daysLeftLabel = computed(() => {
  const n = props.subscription.daysLeft || 0
  return `${n} ${pluralize(n, ['день', 'дня', 'дней'])}`
})

const progressWidth = computed(() => {
  const total = props.subscription.totalMonths || 1
  const used = props.subscription.usedMonths || 0
  return `${Math.min(100, Math.round((used / total) * 100))}%`
})

const featureColumns = computed(() => {
  const list = props.subscription.features || []
  const mid = Math.ceil(list.length / 2)
  return [list.slice(0, mid), list.slice(mid)]
})

function openEdit(focusKey) {
  draft.value = { ...form.value }
  pendingFocusKey.value = typeof focusKey === 'string' && focusKey ? focusKey : null
  editOpen.value = true
}

async function onEditShow() {
  const key = pendingFocusKey.value
  pendingFocusKey.value = null
  if (!key) return
  await nextTick()
  editFormRef.value?.focusField(key)
}

async function saveEdit() {
  saving.value = true
  try {
    const payload = { ...draft.value }
    delete payload.ogrnSpacer
    await settingsApi.update({ service: payload })
    form.value = { ...form.value, ...payload }
    editOpen.value = false
    savedOpen.value = true
    emit('saved', payload)
  } finally {
    saving.value = false
  }
}

function openBrandingEdit() {
  brandingDraft.value = {
    logo: '',
    description: form.value.description || ''
  }
  brandingEditOpen.value = true
}

function onLogoPick(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    brandingDraft.value.logo = String(reader.result || '')
  }
  reader.readAsDataURL(file)
  event.target.value = ''
}

async function saveBranding() {
  brandingSaving.value = true
  try {
    const payload = {
      logo: brandingDraft.value.logo || form.value.logo || '',
      description: brandingDraft.value.description
    }
    await settingsApi.update({ service: payload })
    form.value = { ...form.value, ...payload }
    brandingEditOpen.value = false
    savedOpen.value = true
    emit('saved', payload)
  } finally {
    brandingSaving.value = false
  }
}

defineExpose({ openEdit })
</script>

<style scoped lang="scss">
@use './settingsShared.scss';

.settings-card--subscription {
  background: linear-gradient(301.84deg, #051b54 3.25%, #0b3cba 114.95%);
}

.settings-card :deep(.base-form) {
  flex: none;
  gap: 0;
  overflow: visible;
}

.settings-card :deep(.base-form__body) {
  flex: none;
  max-height: none;
  overflow: visible;
}

.settings-card :deep(.base-form__scroll) {
  overflow: visible;
  gap: 20px;
}

.settings-card :deep(.base-form-block__fields) {
  gap: 15px;
}

.service-edit {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  min-height: 0;
  flex: 1;
  overflow: hidden;
}

.service-edit__title {
  margin: 0;
  flex-shrink: 0;
  color: var(--dvijok-bg-dark);
  font-size: 16px;
  font-weight: 600;
  line-height: 19px;
  text-transform: uppercase;
}

.service-edit__scroll {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    width: 0;
    height: 0;
    display: none;
  }
}

.service-edit__scroll :deep(.base-form__scrollbar) {
  display: none;
}

.service-edit__scroll :deep(.base-form) {
  flex: none;
  gap: 0;
  overflow: visible;
}

.service-edit__scroll :deep(.base-form__body) {
  flex: none;
  max-height: none;
  overflow: visible;
}

.service-edit__scroll :deep(.base-form__scroll) {
  overflow: visible;
  gap: 40px;
}

.service-edit__scroll :deep(.base-form-block__fields) {
  gap: 15px;
}

.service-edit__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.service-saved {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.service-saved__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}

.subscription__status-row {
  display: flex;
  align-items: center;
  gap: 35px;
}

.subscription__pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border: 1px solid;
  border-radius: 50px;
  font-size: 12px;
  font-weight: 600;
  line-height: 15px;
  white-space: nowrap;
}

.subscription__meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.subscription__meta-label {
  color: #7f9ad1;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.subscription__meta-value {
  color: var(--dvijok-white);
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
}

.subscription__usage {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subscription__progress {
  width: 100%;
  height: 6px;
  border-radius: 50px;
  background: #c0d0ff;
  overflow: hidden;
}

.subscription__progress-fill {
  height: 6px;
  border-radius: 50px;
  background: #3b82f6;
}

.subscription__features {
  display: flex;
  gap: 20px;
}

.subscription__features-col {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: fit-content;
  flex-shrink: 0;
}

.subscription__feature {
  display: flex;
  align-items: center;
  gap: 10px;
}

.subscription__feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.subscription__feature-icon img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.subscription__change {
  width: 100%;

  &:not(:disabled):not(.q-btn--disabled):hover {
    color: var(--dvijok-white) !important;
    background: var(--dvijok-text-secondary) !important;
    box-shadow: inset 0 0 0 2px transparent !important;
  }

  &:not(:disabled):not(.q-btn--disabled):active {
    color: var(--dvijok-text-secondary) !important;
    background: var(--dvijok-white) !important;
    box-shadow: inset 0 0 0 2px var(--dvijok-text-secondary) !important;
  }
}

.branding {
  display: flex;
  gap: 30px;
}

.branding__logo-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: fit-content;
  flex-shrink: 0;
}

.branding__desc-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.branding__label {
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.branding__logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border: 1px dashed var(--dvijok-text-secondary);
  border-radius: 6px;
  box-sizing: border-box;
  overflow: hidden;

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.branding__desc {
  width: 100%;
  padding: 14px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
  box-sizing: border-box;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.branding-edit {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.branding-edit__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 16px;
  font-weight: 600;
  line-height: 19px;
  text-transform: uppercase;
}

.branding-edit__body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.branding-edit__logos {
  display: flex;
  flex-direction: row;
  gap: 60px;
  width: 100%;
}

.branding-edit__col {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.branding-edit__label {
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.branding-edit__drop {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100px;
  border: 1px dashed var(--dvijok-text-secondary);
  border-radius: 6px;
  background: var(--dvijok-choice-active);
  box-sizing: border-box;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  text-align: center;
  overflow: hidden;
}

.branding-edit__file {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.branding-edit__drop-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}

.branding-edit__prev {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border: 1px dashed var(--dvijok-text-secondary);
  border-radius: 6px;
  box-sizing: border-box;
  overflow: hidden;

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.branding-edit__desc-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.branding-edit__desc {
  width: 100%;
  min-height: 80px;
  padding: 14px;
  border: 1px solid var(--dvijok-text-secondary);
  border-radius: 10px;
  box-sizing: border-box;
  resize: vertical;
  background: var(--dvijok-white);
  font-family: inherit;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-bg-dark);

  &::placeholder {
    color: var(--dvijok-text-secondary);
  }

  &:focus {
    outline: none;
    border-color: var(--dvijok-bg-dark);
  }
}

.branding-edit__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
</style>
