<template>
  <q-page class="register">
    <AuthSidebar mode="register" @toggle="goLogin" />

    <section class="register__main">
      <div class="register__content">
        <div class="register__card">
          <div class="register__heading">
            <h1 class="register__title">Регистрация автосервиса</h1>
            <p class="register__subtitle">Заполните данные о вашей организации</p>
          </div>

          <div class="register__form-wrap">
            <BaseForm ref="formRef" v-model="form" :blocks="blocks" />
          </div>
        </div>

        <div class="register__actions">
          <div class="register__consent">
            <BaseCheckbox v-model="form.consent" />
            <p class="register__consent-text">
              Я принимаю
              <a
                class="register__link"
                :href="offerDocument.href"
                target="_blank"
                rel="noopener noreferrer"
                >{{ offerDocument.consentLabel }}</a
              >
              и ознакомился с
              <template v-for="(doc, index) in reviewDocuments" :key="doc.id">
                <a
                  class="register__link"
                  :href="doc.href"
                  target="_blank"
                  rel="noopener noreferrer"
                  >{{ doc.consentLabel }}</a
                >{{ reviewSeparator(index) }}
              </template>
            </p>
          </div>

          <p v-if="errorMessage" class="register__error">{{ errorMessage }}</p>
          <BaseButton
            class="register__submit"
            color="blue1"
            scheme="solid-light-outlined"
            size="lg"
            block
            :loading="loading"
            :disable="!form.consent"
            @click="onSubmit"
          >
            Зарегистрировать автосервис
          </BaseButton>
        </div>
      </div>

      <p class="register__support">Техподдержка: support@dvijok.ru · 8 800 000-00-00</p>
    </section>

    <BaseModal v-model="success" persistent>
      <div class="register__success">
        <h2 class="register__success-title">Ваш автосервис зарегистрирован!</h2>
        <BaseButton color="blue1" scheme="solid-light-outlined" size="lg" @click="goToSystem">
          Перейти в систему
        </BaseButton>
      </div>
    </BaseModal>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthSidebar from '@/components/auth/AuthSidebar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseForm from '@/components/ui/BaseForm.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { requiredPhone } from '@/composables/useFormValidation.js'
import { PLATFORM_DOCUMENTS } from '@/constants/platformDocuments.js'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const offerDocument = PLATFORM_DOCUMENTS.find(doc => doc.id === 'offer')
const reviewDocuments = PLATFORM_DOCUMENTS.filter(doc => doc.id !== 'offer')

function reviewSeparator(index) {
  if (index < reviewDocuments.length - 2) return ', '
  if (index === reviewDocuments.length - 2) return ' и '
  return '.'
}

const form = ref({
  name: '',
  headName: '',
  legalType: 'ИП',
  inn: '',
  taxSystem: 'УСН',
  phone: '',
  email: '',
  contactName: '',
  address: '',
  password: '',
  passwordConfirm: '',
  consent: false
})

const formRef = ref(null)

function formatPhone(raw) {
  let d = String(raw || '').replace(/\D/g, '')
  if (!d) return ''
  if (d[0] === '8') d = '7' + d.slice(1)
  if (d[0] !== '7') d = '7' + d
  d = d.slice(0, 11)
  const out = ['+' + d[0]]
  if (d.length > 1) out.push(d.slice(1, 4))
  if (d.length > 4) out.push(d.slice(4, 7))
  if (d.length > 7) out.push(d.slice(7, 9))
  if (d.length > 9) out.push(d.slice(9, 11))
  return out.filter(Boolean).join(' ')
}

const blocks = [
  {
    title: 'Об организации',
    fields: [
      {
        key: 'name',
        label: 'Название автосервиса',
        placeholder: 'Введите название',
        required: true,
        requiredMessage: 'Введите название автосервиса'
      },
      {
        key: 'headName',
        label: 'ФИО руководителя',
        placeholder: 'Введите ФИО',
        required: true,
        requiredMessage: 'Введите ФИО руководителя'
      }
    ]
  },
  {
    title: 'Юридические данные',
    fields: [
      {
        key: 'legalType',
        label: 'Тип юридического лица',
        type: 'choice',
        shape: 'pill',
        options: [
          { label: 'ИП', value: 'ИП' },
          { label: 'ООО', value: 'ООО' },
          { label: 'ОАО', value: 'ОАО' },
          { label: 'ЗАО', value: 'ЗАО' },
          { label: 'ПАО', value: 'ПАО' }
        ]
      },
      {
        key: 'inn',
        label: 'ИНН',
        placeholder: '123456789123',
        row: 'legal',
        required: true,
        requiredMessage: 'Введите ИНН',
        validate: value => {
          const innDigits = String(value || '').replace(/\D/g, '')
          return innDigits.length < 10 ? 'ИНН должен содержать минимум 10 цифр' : ''
        }
      },
      {
        key: 'taxSystem',
        label: 'Система налогообложения',
        type: 'choice',
        row: 'legal',
        options: [
          { label: 'УСН (упрощенная)', value: 'УСН' },
          { label: 'НДС 20%', value: 'НДС' }
        ]
      }
    ]
  },
  {
    title: 'Контакты и адрес',
    fields: [
      {
        key: 'phone',
        label: 'Номер телефона',
        placeholder: '+7 999 999 99 99',
        transform: formatPhone,
        validate: requiredPhone('Введите телефон в формате +7 999 999 99 99')
      },
      {
        key: 'email',
        label: 'Адрес электронной почты',
        placeholder: 'Введите почту',
        validate: value =>
          /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '')) ? '' : 'Введите корректный email'
      },
      {
        key: 'contactName',
        label: 'ФИО контактного лица',
        placeholder: 'Введите ФИО',
        required: true,
        requiredMessage: 'Введите ФИО контактного лица'
      },
      {
        key: 'address',
        label: 'Фактический адрес',
        placeholder: 'Введите адрес',
        required: true,
        requiredMessage: 'Введите адрес'
      },
      {
        key: 'password',
        label: 'Придумайте пароль',
        placeholder: 'Пароль',
        type: 'password',
        validate: value =>
          String(value || '').length < 6 ? 'Пароль должен быть не менее 6 символов' : ''
      },
      {
        key: 'passwordConfirm',
        label: 'Повторите пароль',
        placeholder: 'Пароль',
        type: 'password',
        validate: value => (value !== form.value.password ? 'Пароли не совпадают' : '')
      }
    ]
  }
]

const loading = ref(false)
const success = ref(false)
const errorMessage = ref('')

function goLogin() {
  router.push({ name: 'login' })
}

function goToSystem() {
  success.value = false
  router.push(authStore.homeRoute)
}

async function onSubmit() {
  if (formRef.value?.validate() === false) return
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.register(form.value)
    success.value = true
  } catch (err) {
    errorMessage.value = err?.data?.message || 'Не удалось зарегистрироваться'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.register__main {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  overflow: hidden;
}

.register__content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 680px;
  max-height: 100%;
  min-height: 0;
}

.register__card {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 100%;
  min-height: 0;
  padding: 30px;
  overflow: hidden;
  background-color: var(--dvijok-white);
  border-radius: 15px;
}

.register__heading {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.register__form-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.register__actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.register__consent {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.register__consent-text {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
  text-align: left;
}

.register__link {
  color: #2a4ec4;
  text-decoration: underline;
}

.register__link:hover {
  color: var(--dvijok-link-hover);
}

.register__submit:disabled,
.register__submit.q-btn--disabled {
  opacity: 1 !important;
  color: var(--dvijok-white) !important;
  background: #888888 !important;
  box-shadow: none !important;
}

.register__error {
  margin: 0;
  color: var(--dvijok-danger);
  font-size: 13px;
  font-weight: 500;
  line-height: 16px;
  text-align: center;
}

.register__title {
  margin: 0;
  color: var(--dvijok-text-heading);
  font-size: 32px;
  font-weight: 700;
  line-height: 39px;
  text-align: start;
}

.register__subtitle {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
  text-align: start;
}

.register__support {
  position: absolute;
  bottom: 20px;
  margin: 0;
  color: var(--dvijok-text-tertiary);
  font-size: 11px;
  font-weight: 500;
  line-height: 13px;
}

.register__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.register__success-title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}
</style>
