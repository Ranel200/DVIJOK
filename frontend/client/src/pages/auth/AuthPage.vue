<template>
  <q-page class="auth-page">
    <AppBlock :title="formTitle" subtitle="Заполните поля">
      <form class="auth-form" @submit.prevent="onSubmit">
        <BaseField
          v-if="!isLogin"
          v-model="form.name"
          label="Введите ваши фамилию и имя"
          placeholder="Иванов Иван"
          block
        />

        <BaseField
          v-model="form.phone"
          label="Введите номер телефона"
          placeholder="+7 999 999 99 99"
          mask="+7 ### ### ## ##"
          block
        />

        <BaseButton color="blue1" size="sm" type="button" @click="onSendCode">
          Отправить код
        </BaseButton>

        <div class="auth-form__code">
          <p class="auth-form__code-label">Введите код</p>
          <CodeInputs v-model="form.code" />
        </div>

        <BaseButton color="green" size="sm" type="submit" :loading="loading">
          {{ submitLabel }}
        </BaseButton>
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
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import CodeInputs from '@/components/ui/CodeInputs.vue'
import { useAuthStore } from '@/stores/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  name: '',
  phone: '',
  code: ''
})
const loading = ref(false)

const isLogin = computed(() => route.name === 'login')
const formTitle = computed(() => (isLogin.value ? 'Вход в аккаунт' : 'Регистрация'))
const submitLabel = computed(() => (isLogin.value ? 'Войти' : 'Зарегистрироваться'))
const toggleTitle = computed(() => (isLogin.value ? 'Еще нет аккаунта?' : 'Уже есть аккаунт?'))
const toggleLabel = computed(() => (isLogin.value ? 'Зарегистрироваться' : 'Войти'))

function goToggle() {
  router.push({ name: isLogin.value ? 'register' : 'login' })
}

function onSendCode() {}

async function onSubmit() {
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

.auth-form__code {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-form__code-label {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
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
