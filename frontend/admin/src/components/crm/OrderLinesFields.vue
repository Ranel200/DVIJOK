<template>
  <BaseFormBlock class="order-form__details" title="Детали заказа" stack-fields>
    <div class="order-form__lines" :class="{ 'order-form__lines--wide': wide }">
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
        <BaseButton color="blue2" size="sm" class="order-form__line-btn" @click="emit('add')">
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
              @click="emit('remove', index)"
            >
              Удалить
            </BaseButton>
          </div>
        </div>
      </div>
    </div>
  </BaseFormBlock>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import { formatCrmMoney } from '@/constants/crm.js'
import { formatSurnameInitial } from '@/utils/name.js'

const props = defineProps({
  draft: {
    type: Object,
    required: true
  },
  lineDraft: {
    type: Object,
    required: true
  },
  serviceOptions: {
    type: Array,
    default: () => []
  },
  masterOptions: {
    type: Array,
    default: () => []
  },
  wide: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'remove'])

function formatLineIndex(index) {
  return String(index + 1).padStart(2, '0')
}

function optionLabel(options, value, fallback = '—') {
  return options.find(item => item.value === value)?.label || fallback
}

function lineServiceLabel(line) {
  return optionLabel(props.serviceOptions, line.serviceId)
}

function lineMasterLabel(line) {
  return formatSurnameInitial(optionLabel(props.masterOptions, line.masterId, '')) || '—'
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
</script>

<style scoped lang="scss">
.order-form__lines {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
  max-width: 600px;
}

.order-form__lines--wide {
  max-width: none;
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

  :deep(.base-input .q-field__control) {
    padding: 10px 15px;
  }
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
