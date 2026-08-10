<template>
  <q-page class="login">
    <AuthSidebar mode="login" @toggle="goRegister" />

    <section class="login__main">
      <div class="login__card">
        <div class="login__heading">
          <h1 class="login__title">Вход в систему</h1>
          <p class="login__subtitle"> Введите данные вашего аккаунта </p>
        </div>

        <BaseField
          v-model="form.login"
          class="login__field"
          label="Телефон или почта"
          placeholder="Телефон или почта"
          block
        />

        <BaseField
          v-model="form.password"
          class="login__field"
          :type="showPassword ? 'text' : 'password'"
          label="Пароль"
          placeholder="Пароль"
          block
        >
          <template #append>
            <q-btn
              flat
              dense
              type="button"
              class="login__eye-btn"
              :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              @click="showPassword = !showPassword"
            >
              <EyeIcon :closed="showPassword" />
            </q-btn>
          </template>
        </BaseField>

        <div class="login__options">
          <div class="login__options-left">
            <BaseCheckbox v-model="remember" />
            <BaseButton color="blue1" text @click="onRemember">Запомнить меня</BaseButton>
          </div>
          <div class="login__options-right">
            <BaseButton color="blue1" text @click="onForgotPassword">Забыли пароль?</BaseButton>
          </div>
        </div>

        <div class="login__actions">
          <p v-if="errorMessage" class="login__error">{{ errorMessage }}</p>
          <BaseButton
            color="blue1"
            scheme="solid-light-outlined"
            size="lg"
            block
            :loading="loading"
            @click="onSubmit"
          >
            Войти в систему
          </BaseButton>

          <span class="login__or">или</span>

          <BaseButton
            color="blue1"
            scheme="outlined-solid-light"
            size="lg"
            block
            @click="goRegister"
          >
            Зарегистрироваться
          </BaseButton>
        </div>
      </div>

      <p class="login__support">Техподдержка: support@dvijok.ru · 8 800 000-00-00</p>
    </section>
  </q-page>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthSidebar from '@/components/auth/AuthSidebar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseField from '@/components/ui/BaseField.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  login: '',
  password: ''
})
const showPassword = ref(false)
const loading = ref(false)
const remember = ref(false)
const errorMessage = ref('')

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await authStore.login({
      email: form.login,
      password: form.password,
      remember: remember.value
    })
    router.push(authStore.homeRoute)
  } catch (err) {
    errorMessage.value = err?.data?.message || 'Не удалось войти'
  } finally {
    loading.value = false
  }
}

function goRegister() {
  router.push({ name: 'register' })
}

function onRemember() {
  remember.value = !remember.value
}

function onForgotPassword() {}
</script>

<style scoped lang="scss">
.login {
  display: flex;
  min-height: 100vh;
}

.login__main {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login__card {
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
  max-width: 680px;
  padding: 75px;
  background-color: var(--dvijok-white);
  border-radius: 15px;
}

.login__heading {
  display: flex;
  flex-direction: column;
}

.login__title {
  margin: 0;
  color: var(--dvijok-text-heading);
  font-size: 32px;
  font-weight: 700;
  line-height: 39px;
  text-align: center;
}

.login__subtitle {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-size: 16px;
  font-weight: 400;
  line-height: 19px;
  text-align: center;
}

.login__field {
  width: 100%;
}

.login__options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.login__options-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.login__options-right {
  display: flex;
  align-items: center;
}

.login__actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.login__error {
  margin: 0 0 5px;
  color: var(--dvijok-danger);
  font-size: 13px;
  font-weight: 500;
  line-height: 16px;
  text-align: center;
}

.login__or {
  text-align: center;
  color: var(--dvijok-text-secondary);
  font-size: 12px;
  line-height: 17px;
}

.login__eye-btn {
  min-height: auto;
  padding: 0;

  :deep(.q-btn__content) {
    padding: 0;
  }
}

.login__support {
  position: absolute;
  bottom: 20px;
  margin: 0;
  color: var(--dvijok-text-tertiary);
  font-size: 11px;
  font-weight: 500;
  line-height: 13px;
}
</style>
