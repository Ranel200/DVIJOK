<template>
  <div class="settings">
    <div class="settings__col">
      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Данные автосервиса</h2>
          <button type="button" class="settings-card__edit" aria-label="Редактировать">
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
          <button type="button" class="settings-card__edit" aria-label="Редактировать">
            <img src="/admin/icons/services/edit.svg" alt="" />
          </button>
        </div>
        <div class="branding">
          <div class="branding__logo-block">
            <span class="branding__label">Ваш логотип</span>
            <div class="branding__logo" aria-hidden="true" />
          </div>
          <div class="branding__desc-block">
            <span class="branding__label">Описание автосервиса</span>
            <div class="branding__desc">{{ form.description }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseForm from '@/components/ui/BaseForm.vue'
import Radio from '@/components/ui/Radio.vue'
import { formatRuDate } from '@/utils/formatDateRu.js'
import { pluralize } from '@/utils/pluralize.js'

const form = defineModel('form', { type: Object, required: true })

const props = defineProps({
  subscription: {
    type: Object,
    required: true
  }
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
        shape: 'pill',
        block: false,
        row: 'legal',
        options: form.value.taxSystem
          ? [{ label: form.value.taxSystem, value: form.value.taxSystem }]
          : []
      },
      { key: 'inn', label: 'ИНН', row: 'ids' },
      { key: 'ogrn', label: 'ОГРН', row: 'ids' }
    ]
  },
  {
    title: '',
    fields: [{ key: 'phone', label: 'Номер телефона' }]
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
}

.settings-card :deep(.base-form-block__fields) {
  gap: 15px;
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
  width: 64px;
  height: 64px;
  border: 1px dashed var(--dvijok-text-secondary);
  border-radius: 6px;
  box-sizing: border-box;
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
</style>
