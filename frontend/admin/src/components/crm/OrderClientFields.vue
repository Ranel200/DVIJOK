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
      block
    />
    <BaseField
      v-model="draft.phone"
      layout="horizontal"
      label="Номер"
      placeholder="+7 000 000-00-00"
      mask="+7 ### ###-##-##"
      :readonly="readonly"
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
    <div class="order-client-fields__h-field">
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
      />
    </div>
  </BaseFormBlock>
</template>

<script setup>
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'

defineProps({
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
  blockClass: {
    type: String,
    default: ''
  }
})
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
