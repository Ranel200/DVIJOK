<template>
  <BaseModal
    :model-value="modelValue"
    size="panel"
    :title="modalTitle"
    persistent
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="service-form">
      <div class="service-form__col">
        <BaseFormBlock
          class="service-form__block service-form__block--main"
          title="Основная информация"
          layout="horizontal"
        >
          <BaseField
            v-model="draft.title"
            layout="horizontal"
            label="Название"
            placeholder="Название услуги"
            block
          />
          <BaseField
            v-model="draft.description"
            class="service-form__textarea"
            layout="horizontal"
            type="textarea"
            label="Описание"
            placeholder="Введите описание услуги"
            block
          />
          <div class="service-form__h-field">
            <span class="service-form__label">Категория</span>
            <BaseSelect
              v-model="draft.category"
              :options="categoryOptions"
              placeholder="Выберите категорию"
              block
            />
          </div>
        </BaseFormBlock>

        <BaseFormBlock
          class="service-form__block service-form__block--pricing"
          title="Стоимость и время"
          layout="horizontal"
        >
          <div class="service-form__h-field service-form__h-field--choice">
            <span class="service-form__label">Тип цены</span>
            <BaseChoice
              v-model="draft.priceType"
              :options="priceTypeOptions"
              shape="pill"
              :block="false"
              gap="10px"
            />
          </div>
          <BaseField
            v-model="draft.price"
            layout="horizontal"
            type="number"
            label="Цена"
            placeholder="0"
            block
          />
          <div class="service-form__h-field">
            <span class="service-form__label">Длительность</span>
            <div class="service-form__duration">
              <BaseInput v-model="draft.duration" type="number" placeholder="0" block />
              <BaseSelect
                v-model="draft.durationUnit"
                :options="durationUnitOptions"
                hide-chevron
                align="center"
                block
              />
            </div>
          </div>
          <div class="service-form__h-field service-form__h-field--status">
            <span class="service-form__label">Статус</span>
            <button
              type="button"
              :class="['service-form__status', `service-form__status--${draft.status}`]"
              @click="toggleStatus"
            >
              {{ statusLabel }}
            </button>
          </div>
        </BaseFormBlock>
      </div>

      <div class="service-form__col">
        <BaseFormBlock title="Мастера" layout="horizontal" stack-fields>
          <div
            class="service-form__masters"
            :class="{ 'service-form__masters--scroll': draft.masters.length > 4 }"
          >
            <div
              v-for="(masterId, index) in draft.masters"
              :key="index"
              class="service-form__master-row"
            >
              <div class="service-form__master-select">
                <BaseSelect
                  v-model="draft.masters[index]"
                  :options="masterOptions"
                  placeholder="Все сотрудники"
                  block
                />
              </div>
              <BaseButton
                color="red"
                size="sm"
                class="service-form__master-remove"
                :class="{ 'service-form__master-remove--hidden': index === 0 }"
                :tabindex="index === 0 ? -1 : 0"
                :aria-hidden="index === 0"
                @click="removeMaster(index)"
              >
                Удалить
              </BaseButton>
            </div>
          </div>
          <BaseButton color="blue2" size="sm" class="service-form__add-master" @click="addMaster">
            Добавить мастера
          </BaseButton>
        </BaseFormBlock>

        <div class="service-form__notes">
          <div class="service-form__master-row">
            <div class="service-form__master-select">
              <BaseField
                v-model="draft.notes"
                class="service-form__textarea"
                type="textarea"
                label="Заметки по услуге"
                placeholder="Внутренние заметки по услуге"
                block
              />
            </div>
            <BaseButton
              color="red"
              size="sm"
              class="service-form__master-remove service-form__master-remove--hidden"
              tabindex="-1"
              aria-hidden="true"
            >
              Удалить
            </BaseButton>
          </div>
        </div>
      </div>
    </div>

    <template #actions>
      <BaseButton color="red" size="lg" @click="emit('update:modelValue', false)">
        Отмена
      </BaseButton>
      <BaseButton color="green" size="lg" :loading="saving" @click="onSave">
        {{ isEdit ? 'Сохранить изменения' : 'Добавить услугу' }}
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  service: {
    type: Object,
    default: null
  },
  employees: {
    type: Array,
    default: () => []
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const categoryOptions = [
  { value: 'maintenance', label: 'ТО' },
  { value: 'diagnostics', label: 'Диагностика' },
  { value: 'repair', label: 'Ремонт' },
  { value: 'body', label: 'Кузовные работы' },
  { value: 'other', label: 'Прочее' }
]

const priceTypeOptions = [
  { label: 'Фиксированная', value: 'fixed' },
  { label: 'От/До', value: 'range' },
  { label: 'Договорная', value: 'negotiable' }
]

const durationUnitOptions = [
  { value: 'minutes', label: 'Минут' },
  { value: 'hours', label: 'Часов' }
]

const draft = reactive(createEmptyDraft())

const isEdit = computed(() => Boolean(props.service?.id))

const modalTitle = computed(() => {
  if (isEdit.value) {
    return `Редактировать услугу "${props.service.title}"`
  }
  return 'Новая услуга'
})

const statusLabel = computed(() => (draft.status === 'hidden' ? 'Скрыта' : 'Активна'))

const masterOptions = computed(() => [
  { value: 'all', label: 'Все сотрудники' },
  ...props.employees.map(employee => ({
    value: employee.id,
    label: `${employee.name} — ${employee.role}`
  }))
])

watch(
  () => [props.modelValue, props.service],
  ([open]) => {
    if (!open) return
    Object.assign(draft, props.service ? draftFromService(props.service) : createEmptyDraft())
  }
)

function createEmptyDraft() {
  return {
    title: '',
    description: '',
    category: '',
    priceType: 'fixed',
    price: '',
    duration: '',
    durationUnit: 'minutes',
    status: 'active',
    masters: ['all'],
    notes: ''
  }
}

function draftFromService(service) {
  const durationHours = Number(service.durationHours) || 0
  const useMinutes = durationHours > 0 && durationHours < 1
  return {
    title: service.title || '',
    description: service.description || '',
    category: service.category || '',
    priceType: service.priceType || 'fixed',
    price: service.price != null ? String(service.price) : '',
    duration: useMinutes
      ? String(Math.round(durationHours * 60))
      : durationHours
        ? String(durationHours)
        : '',
    durationUnit: useMinutes ? 'minutes' : 'hours',
    status: service.status === 'hidden' ? 'hidden' : 'active',
    masters:
      Array.isArray(service.masters) && service.masters.length
        ? service.masters.map(item => item.id ?? item)
        : service.master?.id
          ? [service.master.id]
          : ['all'],
    notes: service.notes || ''
  }
}

function toggleStatus() {
  draft.status = draft.status === 'hidden' ? 'active' : 'hidden'
}

function addMaster() {
  draft.masters.push('all')
}

function removeMaster(index) {
  if (index === 0) return
  draft.masters.splice(index, 1)
}

function onSave() {
  emit('save', {
    ...draft,
    price: draft.price === '' ? 0 : Number(draft.price),
    duration: draft.duration === '' ? 0 : Number(draft.duration),
    masters: [...draft.masters]
  })
}
</script>

<style scoped lang="scss">
.service-form {
  --dvijok-form-block-title: var(--dvijok-white);
  --dvijok-form-label: var(--dvijok-text-secondary);

  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 50px;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.service-form__col {
  flex: 1;
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

.service-form__block--main {
  width: 70%;
}

.service-form__block--pricing {
  width: 90%;
}

.service-form__h-field {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  column-gap: 15px;
  width: 100%;
}

.service-form__label {
  grid-column: 1;
  color: var(--dvijok-form-label, var(--dvijok-text-secondary));
  font-size: 14px;
  line-height: 16px;
  white-space: nowrap;
}

.service-form__h-field > :not(.service-form__label) {
  grid-column: 2;
  min-width: 0;
  width: 100%;
}

.service-form__h-field--choice > :not(.service-form__label),
.service-form__h-field--status > :not(.service-form__label) {
  width: auto;
  justify-self: start;
}

.service-form__duration {
  display: flex;
  align-items: stretch;
  gap: 10px;
  width: 100%;
}

.service-form__duration > * {
  flex: 1;
  min-width: 0;
}

.service-form__status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  max-width: max-content;
  padding: 10px 25px;
  box-sizing: border-box;
  border-radius: 50px;
  border-style: solid;
  border-width: 1px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  text-align: center;
  white-space: nowrap;
}

.service-form__status--active {
  background-color: var(--dvijok-success-bg);
  color: var(--dvijok-success);
  border-color: var(--dvijok-success);
}

.service-form__status--hidden {
  background-color: var(--dvijok-muted);
  color: var(--dvijok-text-secondary);
  border-color: var(--dvijok-text-secondary);
}

.service-form__textarea {
  :deep(textarea.q-field__native) {
    max-height: calc(16px * 10);
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

.service-form__notes {
  width: 100%;
}

.service-form__notes .service-form__master-row {
  align-items: flex-end;
}

.service-form__masters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.service-form__masters--scroll {
  max-height: calc(4 * 42px + 3 * 10px);
  overflow-x: visible;
  overflow-y: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    width: 0;
    height: 0;
    display: none;
  }
}

.service-form__master-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.service-form__master-select {
  flex: 1;
  min-width: 0;
}

.service-form__master-remove--hidden {
  visibility: hidden;
  pointer-events: none;
}

.service-form__add-master {
  align-self: flex-start;
}
</style>
