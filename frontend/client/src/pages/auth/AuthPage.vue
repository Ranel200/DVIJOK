<template>
  <q-page class="auth-page">
    <AppBlock :title="formTitle" :subtitle="formSubtitle">
      <form class="auth-form" @submit.prevent="onPrimaryAction">
        <template v-if="step === 'name'">
          <BaseField
            v-model="form.name"
            label="Введите ваши фамилию и имя"
            placeholder="Иванов Иван"
            block
          />

          <BaseButton color="blue1" size="sm" block type="submit" :disable="!canProceedName">
            Далее
          </BaseButton>
        </template>

        <template v-else-if="step === 'phone'">
          <BaseField
            v-model="form.phone"
            placeholder="+7 999 999 99 99"
            mask="+7 ### ### ## ##"
            block
          />

          <div v-if="!isLogin" class="auth-form__consents">
            <BaseCheckbox v-model="form.acceptTerms">
              Я принимаю
              <a
                class="auth-form__link"
                href="/docs/user-agreement.html"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
                >Пользовательское соглашение</a
              >
              и ознакомился с
              <a
                class="auth-form__link"
                href="/docs/privacy-policy.html"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
                >Политикой обработки персональных данных</a
              >
            </BaseCheckbox>

            <BaseCheckbox v-model="form.consentPersonal">
              Я даю согласие на
              <a
                class="auth-form__link"
                href="/docs/consent-personal-data.html"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
                >обработку персональных данных</a
              >
            </BaseCheckbox>

            <BaseCheckbox v-model="form.consentTransfer">
              Я даю согласие на
              <a
                class="auth-form__link"
                href="/docs/consent-transfer-autoservice.html"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
                >передачу моих данных выбранному автосервису</a
              >
            </BaseCheckbox>

            <BaseCheckbox v-model="form.consentMarketing">
              Хочу получать информацию об
              <a
                class="auth-form__link"
                href="/docs/consent-marketing.html"
                target="_blank"
                rel="noopener noreferrer"
                @click.stop
                >акциях, скидках и специальных предложениях</a
              >
              ДВИЖОК
            </BaseCheckbox>
          </div>

          <BaseButton
            color="blue1"
            size="sm"
            block
            type="submit"
            :loading="loading"
            :disable="!canProceedPhone"
          >
            Далее
          </BaseButton>
        </template>

        <template v-else>
          <CodeInputs v-model="form.code" />

          <button type="button" class="auth-form__alt-phone" @click="onChangePhone">
            {{ changePhoneLabel }}
          </button>

          <BaseButton
            color="green"
            size="sm"
            block
            type="submit"
            :loading="loading"
            :disable="form.code.length < 4"
          >
            {{ submitLabel }}
          </BaseButton>
        </template>
      </form>
    </AppBlock>

    <AppBlock variant="dark" :title="toggleTitle">
      <BaseButton color="blue2" size="sm" @click="goToggle">
        {{ toggleLabel }}
      </BaseButton>
    </AppBlock>

    <AppBlock fixed-height class="auth-page__promo">
      <div class="auth-promo">
        <img class="auth-promo__img" src="/client/icons/auth/img.svg" alt="" />
        <p class="auth-promo__text">Здесь могла бы быть ваша реклама</p>
      </div>
    </AppBlock>
  </q-page>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/index.js'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseField from '@/components/ui/BaseField.vue'
import CodeInputs from '@/components/ui/CodeInputs.vue'
import { useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  name: '',
  phone: '',
  code: '',
  acceptTerms: true,
  consentPersonal: true,
  consentTransfer: true,
  consentMarketing: true
})
const loading = ref(false)
const step = ref('phone')

const isLogin = computed(() => route.name === 'login')
const submitLabel = computed(() => (isLogin.value ? 'Войти' : 'Зарегистрироваться'))
const changePhoneLabel = computed(() =>
  isLogin.value ? 'Войти с другим номером' : 'Зарегистрироваться с другим номером'
)
const toggleTitle = computed(() => (isLogin.value ? 'Еще нет аккаунта?' : 'Уже есть аккаунт?'))
const toggleLabel = computed(() => (isLogin.value ? 'Зарегистрироваться' : 'Войти'))

const formTitle = computed(() => {
  if (step.value === 'code') return 'Введите последние 4 цифры номера'
  if (isLogin.value) return 'Войдите в аккаунт через номер телефона'
  return 'Регистрация'
})

const formSubtitle = computed(() => {
  if (step.value === 'code') {
    return 'Вам поступит звонок. Не отвечайте.\nВведите последние 4 цифры номера звонящего.'
  }
  return 'Получите доступ к личному кабинету сервиса'
})

function isPhoneComplete(phone) {
  return String(phone || '').replace(/\D/g, '').length === 11
}

const canProceedName = computed(() => form.name.trim().length > 0)
const canProceedPhone = computed(() => {
  if (!isPhoneComplete(form.phone)) return false
  if (isLogin.value) return true
  return form.acceptTerms && form.consentPersonal && form.consentTransfer && form.consentMarketing
})

function resetForm() {
  form.name = ''
  form.phone = ''
  form.code = ''
  form.acceptTerms = true
  form.consentPersonal = true
  form.consentTransfer = true
  form.consentMarketing = true
  step.value = isLogin.value ? 'phone' : 'name'
}

watch(isLogin, resetForm, { immediate: true })

function goToggle() {
  router.push({ name: isLogin.value ? 'register' : 'login' })
}

function onChangePhone() {
  form.code = ''
  step.value = 'phone'
}

async function onPrimaryAction() {
  if (step.value === 'name') {
    if (!canProceedName.value) return
    step.value = 'phone'
    return
  }

  if (step.value === 'phone') {
    if (!canProceedPhone.value || loading.value) return
    loading.value = true
    try {
      await authApi.requestCode({
        phone: form.phone,
        name: form.name || undefined
      })
      form.code = ''
      step.value = 'code'
    } finally {
      loading.value = false
    }
    return
  }

  onSubmit()
}

async function onSubmit() {
  if (form.code.length < 4) return
  loading.value = true
  try {
    await authStore.login({
      phone: form.phone,
      code: form.code,
      name: form.name
    })
    await router.push({ name: 'home' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.auth-page {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 100%;
  padding: 25px 15px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.auth-form__consents {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-form__link {
  color: var(--dvijok-link);
  text-decoration: underline;
}

.auth-form__alt-phone {
  align-self: flex-start;
  margin: 0;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-link);
  text-decoration: underline;
  text-align: left;
}

.auth-page__promo {
  justify-content: center;
  align-items: center;
}

.auth-promo {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.auth-promo__img {
  display: block;
  width: 82px;
  height: 82px;
}

.auth-promo__text {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
  text-align: center;
}
</style>
