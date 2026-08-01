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
        v-model="draft.role"
        :options="roleOptions"
        shape="pill"
        variant="glass"
        :block="false"
        :disable="isView"
        gap="10px"
      />
    </template>

    <div class="staff-form">
      <div class="staff-form__col staff-form__col--main">
        <BaseFormBlock
          class="staff-form__block"
          title="Информация о сотруднике"
          layout="horizontal"
        >
          <BaseField
            v-model="draft.name"
            layout="horizontal"
            label="ФИО"
            placeholder="Фамилия Имя Отчество"
            :readonly="isView"
            block
          />
          <BaseField
            v-model="draft.phone"
            layout="horizontal"
            label="Номер"
            placeholder="+7 000 000-00-00"
            mask="+7 ### ###-##-##"
            :readonly="isView"
            block
          />
          <BaseField
            v-model="draft.email"
            layout="horizontal"
            label="Почта"
            placeholder="Электронная почта"
            :readonly="isView"
            block
          />
          <BaseField
            v-model="draft.duties"
            class="staff-form__textarea"
            layout="horizontal"
            type="textarea"
            label="Обязанности"
            placeholder="Обязанности"
            :readonly="isView"
            block
          />
          <BaseField
            :model-value="rateDisplay"
            class="staff-form__rate"
            :class="{ 'staff-form__rate--compact': isView }"
            layout="horizontal"
            label="Ставка"
            placeholder="30 000 ₽"
            :readonly="isView"
            block
            @update:model-value="onRateInput"
          />
          <div
            class="staff-form__h-field staff-form__h-field--color"
            :class="{ 'staff-form__h-field--color-edit': !isView }"
          >
            <span class="staff-form__label">Цвет</span>
            <div class="staff-form__color-row">
              <span
                class="staff-form__color-swatch"
                :style="draft.color ? { backgroundColor: draft.color } : null"
              />
              <button
                v-if="!isView"
                type="button"
                class="staff-form__text-btn"
                @click="colorOpen = true"
              >
                {{ isEdit ? 'Поменять' : 'Назначить' }}
              </button>
            </div>
          </div>
        </BaseFormBlock>

        <BaseFormBlock class="staff-form__block" title="Документы сотрудника">
          <div class="staff-form__docs">
            <div
              v-for="doc in documentFields"
              :key="doc.key"
              class="staff-form__doc-row"
              :class="{
                'staff-form__doc-row--text': !isView,
                'staff-form__doc-row--pdf': isView || isEdit
              }"
            >
              <span class="staff-form__doc-label">{{ doc.label }}</span>
              <div class="staff-form__doc-actions">
                <img
                  v-if="isView || isEdit"
                  class="staff-form__doc-icon"
                  src="/admin/icons/schedule/pdf.svg"
                  alt=""
                />
                <button
                  v-if="!isView"
                  type="button"
                  class="staff-form__text-btn"
                  @click="pickDocument(doc.key)"
                >
                  {{ isEdit ? 'Поменять' : 'Загрузить скан' }}
                </button>
              </div>
            </div>
            <p v-if="!isView" class="staff-form__docs-hint">* — необязательно</p>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            class="staff-form__file-input"
            accept=".pdf,image/*"
            @change="onFileChange"
          />
        </BaseFormBlock>
      </div>

      <div class="staff-form__col staff-form__col--access">
        <BaseFormBlock title="Доступ" stack-fields>
          <div class="staff-form__access">
            <div
              v-for="item in visibleAccessOptions"
              :key="item.key"
              class="staff-form__access-row"
            >
              <span class="staff-form__access-label">{{ item.label }}</span>
              <BaseSwitcher
                v-model="draft.access[item.key]"
                on-label="Откр"
                off-label="Закр"
                :disable="isView"
                :aria-label="item.label"
              />
            </div>
          </div>
        </BaseFormBlock>

        <BaseFormBlock title="Логин и пароль" layout="horizontal">
          <BaseField
            v-model="draft.login"
            layout="horizontal"
            label="Логин"
            placeholder="Логин"
            :readonly="isView"
            block
          />
          <BaseField
            v-model="draft.password"
            layout="horizontal"
            :type="showPassword ? 'text' : 'password'"
            label="Пароль"
            placeholder="Пароль"
            :readonly="isView"
            block
          >
            <template #append>
              <q-btn
                flat
                dense
                type="button"
                class="staff-form__eye-btn"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showPassword = !showPassword"
              >
                <EyeIcon :closed="showPassword" />
              </q-btn>
            </template>
          </BaseField>
        </BaseFormBlock>
      </div>
    </div>

    <template #actions>
      <template v-if="isView">
        <BaseButton color="red" size="lg" @click="emit('delete')">Удалить сотрудника</BaseButton>
        <BaseButton color="blue2" size="lg" @click="emit('edit')">Редактировать</BaseButton>
      </template>
      <template v-else>
        <BaseButton color="red" size="lg" @click="emit('update:modelValue', false)">
          Отмена
        </BaseButton>
        <BaseButton color="green" size="lg" :loading="saving" @click="onSave">
          {{ isEdit ? 'Сохранить изменения' : 'Добавить сотрудника' }}
        </BaseButton>
      </template>
    </template>
  </BaseModal>

  <StaffColorPickerModal v-model="colorOpen" :color="draft.color" @save="onColorSave" />
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import StaffColorPickerModal from '@/components/schedule/StaffColorPickerModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseChoice from '@/components/ui/BaseChoice.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseFormBlock from '@/components/ui/BaseFormBlock.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSwitcher from '@/components/ui/BaseSwitcher.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import {
  STAFF_ACCESS_OPTIONS,
  STAFF_ROLE_LABELS,
  STAFF_ROLE_OPTIONS,
  formatStaffRate,
  mapLegacyRole,
  parseStaffRate
} from '@/constants/staff.js'
import { formatStaffName } from '@/utils/name.js'

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
  employee: {
    type: Object,
    default: null
  },
  saving: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'edit', 'delete'])

const documentFields = [
  { key: 'passport', label: 'Паспорт*' },
  { key: 'inn', label: 'ИНН*' },
  { key: 'medicalBook', label: 'Мед. книжка*' }
]

const draft = reactive(createEmptyDraft())
const colorOpen = ref(false)
const showPassword = ref(false)
const fileInputRef = ref(null)
const pendingDocKey = ref(null)

const isView = computed(() => props.mode === 'view')
const isEdit = computed(() => props.mode === 'edit')

const modalTitle = computed(() => {
  if (props.mode === 'create') return 'Новый сотрудник'
  return formatStaffName(props.employee?.name || draft.name) || 'Сотрудник'
})

const roleOptions = computed(() => {
  if (!isView.value) return STAFF_ROLE_OPTIONS
  const role = draft.role
  const fromList = STAFF_ROLE_OPTIONS.find(item => item.value === role)
  if (fromList) return [fromList]
  return [{ value: role, label: STAFF_ROLE_LABELS[role] || props.employee?.role || 'Сотрудник' }]
})

const visibleAccessOptions = computed(() => {
  if (!isView.value) return STAFF_ACCESS_OPTIONS
  return STAFF_ACCESS_OPTIONS.filter(item => draft.access[item.key])
})

const rateDisplay = computed(() => formatStaffRate(draft.rate))

watch(
  () => [props.modelValue, props.employee, props.mode],
  ([open]) => {
    if (!open) return
    showPassword.value = false
    Object.assign(draft, props.employee ? draftFromEmployee(props.employee) : createEmptyDraft())
  }
)

function emptyAccess() {
  return Object.fromEntries(STAFF_ACCESS_OPTIONS.map(item => [item.key, false]))
}

function emptyDocuments() {
  return { passport: null, inn: null, medicalBook: null }
}

function createEmptyDraft() {
  return {
    role: 'senior_admin',
    name: '',
    phone: '',
    email: '',
    duties: '',
    rate: '',
    color: '',
    documents: emptyDocuments(),
    access: emptyAccess(),
    login: '',
    password: ''
  }
}

function draftFromEmployee(employee) {
  const access = emptyAccess()
  if (employee.access && typeof employee.access === 'object') {
    for (const key of Object.keys(access)) {
      access[key] = Boolean(employee.access[key])
    }
  }
  const documents = emptyDocuments()
  if (employee.documents && typeof employee.documents === 'object') {
    for (const key of Object.keys(documents)) {
      documents[key] = employee.documents[key] || null
    }
  }
  return {
    role: mapLegacyRole(employee.roleKey || employee.role),
    name: employee.name || '',
    phone: employee.phone || '',
    email: employee.email || '',
    duties: employee.duties || '',
    rate: parseStaffRate(employee.rate),
    color: employee.color || employee.avatarBg || '',
    documents,
    access,
    login: employee.login || '',
    password: employee.password || ''
  }
}

function onRateInput(value) {
  if (isView.value) return
  draft.rate = parseStaffRate(value)
}

function onColorSave(color) {
  draft.color = color || ''
}

function pickDocument(key) {
  pendingDocKey.value = key
  const input = fileInputRef.value
  if (!input) return
  input.value = ''
  input.click()
}

function onFileChange(event) {
  const key = pendingDocKey.value
  const file = event.target?.files?.[0]
  pendingDocKey.value = null
  if (!key || !file) return
  draft.documents[key] = { name: file.name, fileName: file.name }
}

function onSave() {
  emit('save', {
    role: draft.role,
    name: draft.name.trim(),
    phone: draft.phone,
    email: draft.email.trim(),
    duties: draft.duties.trim(),
    rate: draft.rate === '' ? null : Number(draft.rate),
    color: draft.color || null,
    documents: { ...draft.documents },
    access: { ...draft.access },
    login: draft.login.trim(),
    password: draft.password
  })
}
</script>

<style scoped lang="scss">
.staff-form {
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

.staff-form__col {
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

.staff-form__col--main {
  flex: 0 1 420px;
  max-width: 420px;
}

.staff-form__col--access {
  flex: 0 1 400px;
  max-width: 400px;
  margin-left: auto;
}

.staff-form :deep(.base-field__label),
.staff-form__label,
.staff-form__doc-label,
.staff-form__access-label {
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.staff-form__h-field {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: 1 / -1;
  align-items: center;
  column-gap: 15px;
  width: 100%;
}

.staff-form__label {
  grid-column: 1;
  white-space: nowrap;
}

.staff-form__h-field > :not(.staff-form__label) {
  grid-column: 2;
  min-width: 0;
}

.staff-form__h-field--color-edit > :not(.staff-form__label) {
  justify-self: end;
  width: auto;
}

.staff-form__h-field--color-edit {
  padding-top: 9px;
  padding-bottom: 9px;
}

.staff-form__color-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: fit-content;
}

.staff-form__color-swatch {
  display: block;
  width: 90px;
  height: 32px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.12);
  flex-shrink: 0;
}

.staff-form__text-btn {
  padding: 0;
  border: none;
  background: transparent;
  color: var(--dvijok-white);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
  text-decoration: underline;
  cursor: pointer;
  white-space: nowrap;

  &:hover {
    opacity: 0.85;
  }

  &:active {
    text-decoration: none;
  }
}

.staff-form__rate--compact :deep(.base-field__control) {
  width: 90px;
  max-width: 90px;
}

.staff-form__textarea {
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

.staff-form__docs {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.staff-form__doc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
}

.staff-form__doc-row--text {
  padding-top: 9px;
  padding-bottom: 9px;
}

.staff-form__doc-row--pdf {
  padding-top: 2.5px;
  padding-bottom: 2.5px;
}

.staff-form__doc-label {
  white-space: nowrap;
}

.staff-form__doc-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.staff-form__doc-icon {
  display: block;
  width: 30px;
  height: 30px;
}

.staff-form__docs-hint {
  margin: 0;
  padding: 10px 10px 10px 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.staff-form__file-input {
  display: none;
}

.staff-form__access {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.staff-form__access-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
  padding-top: 6px;
  padding-bottom: 6px;
}

.staff-form__access-label {
  white-space: nowrap;
}

.staff-form__eye-btn {
  min-height: auto;
  padding: 0;

  :deep(.q-btn__content) {
    padding: 0;
  }
}
</style>
