<template>
  <BaseFormBlock class="order-car-fields" title="Автомобиль" layout="horizontal">
    <BaseField
      v-model="draft.plate"
      layout="horizontal"
      label="Гос. номер"
      placeholder="Гос. номер"
      :readonly="readonly"
      block
    />
    <BaseField
      v-model="draft.brand"
      layout="horizontal"
      label="Марка"
      placeholder="Марка"
      :readonly="readonly"
      block
    />
    <BaseField
      v-model="draft.model"
      layout="horizontal"
      label="Модель"
      placeholder="Модель"
      :readonly="readonly"
      block
    />
    <div class="order-car-fields__h-field">
      <span class="order-car-fields__label">Год/цвет</span>
      <div class="order-car-fields__pair">
        <BaseInput v-model="draft.year" placeholder="Год" :readonly="readonly" block />
        <BaseInput v-model="draft.color" placeholder="Цвет" :readonly="readonly" block />
      </div>
    </div>
    <BaseField
      v-model="draft.vin"
      layout="horizontal"
      label="VIN"
      placeholder="17 символов из ПТС"
      mask="NNNNNNNNNNNNNNNNN"
      :readonly="readonly"
      block
    />
    <BaseField
      v-model="draft.mileage"
      layout="horizontal"
      type="number"
      label="Пробег"
      placeholder="Пробег в км"
      :readonly="readonly"
      block
    />
  </BaseFormBlock>
</template>

<script setup>
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

defineProps({
  draft: {
    type: Object,
    required: true
  },
  readonly: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped lang="scss">
.order-car-fields :deep(.base-field__label),
.order-car-fields__label {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.order-car-fields__h-field {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  column-gap: 15px;
  width: 100%;
}

.order-car-fields__label {
  grid-column: 1;
  white-space: nowrap;
}

.order-car-fields__h-field > :not(.order-car-fields__label) {
  grid-column: 2;
  min-width: 0;
  width: 100%;
}

.order-car-fields__pair {
  display: flex;
  align-items: stretch;
  gap: 10px;
  width: 100%;
}

.order-car-fields__pair > * {
  flex: 1;
  min-width: 0;
}
</style>
