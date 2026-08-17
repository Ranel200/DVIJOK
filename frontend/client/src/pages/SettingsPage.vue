<template>
  <q-page class="settings">
    <ClientHeader title="Настройки" />

    <div class="settings__body">
      <template v-if="isEditing">
        <div class="settings__edit">
          <button type="button" class="settings__back" @click="cancelEdit">
            <ArrowIcon direction="left" :size="14" color="#093095" />
            <span>Вернуться назад</span>
          </button>

          <section class="settings__section" aria-labelledby="settings-edit-title">
            <h2 id="settings-edit-title" class="settings__section-title">
              Обновите данные аккаунта
            </h2>

            <form class="settings__form settings__form--edit" @submit.prevent="onSave">
              <div class="settings__fields">
                <BaseField
                  v-model="form.name"
                  label="Имя Фамилия"
                  placeholder="Иванов Иван"
                  block
                />
                <BaseField
                  v-model="form.phone"
                  label="Номер телефона"
                  placeholder="+7 999 999 99 99"
                  mask="+7 ### ### ## ##"
                  block
                />
                <BaseField
                  v-model="form.email"
                  label="Электронная почта"
                  type="email"
                  placeholder="pochta@mail.ru"
                  block
                />
              </div>

              <BaseButton color="green" size="sm" block type="submit" :loading="saving">
                Сохранить изменения
              </BaseButton>
            </form>
          </section>
        </div>
      </template>

      <template v-else>
        <section class="settings__section" aria-labelledby="settings-account-title">
          <h2 id="settings-account-title" class="settings__section-title">Данные аккаунта</h2>
          <div class="settings__form">
            <BaseField
              :model-value="form.name"
              label="Имя Фамилия"
              placeholder="Иванов Иван"
              block
              readonly
            />
            <BaseField
              :model-value="form.phone"
              label="Номер телефона"
              placeholder="+7 999 999 99 99"
              block
              readonly
            />
            <BaseField
              :model-value="form.email"
              label="Электронная почта"
              placeholder="pochta@mail.ru"
              block
              readonly
            />
          </div>
        </section>

        <button type="button" class="settings__edit-link" @click="startEdit">
          <span>Изменить данные аккаунта</span>
          <span class="settings__edit-icon" aria-hidden="true" />
        </button>

        <section class="settings__section" aria-labelledby="settings-consents-title">
          <h2 id="settings-consents-title" class="settings__section-title">Согласия</h2>
          <div class="settings__list">
            <div v-for="item in consentItems" :key="item.key" class="settings-consent">
              <BaseSwitcher
                v-model="consents[item.key]"
                class="settings-consent__switch"
                :aria-label="item.title"
              />
              <div class="settings-consent__text">
                <p class="settings-consent__title">{{ item.title }}</p>
                <p class="settings-consent__desc">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <BaseButton
          color="red"
          size="sm"
          block
          class="settings__logout"
          :loading="logoutLoading"
          @click="onLogout"
        >
          Выйти
        </BaseButton>

        <section class="settings__section" aria-labelledby="settings-docs-title">
          <h2 id="settings-docs-title" class="settings__section-title">Документы</h2>
          <div class="settings__list">
            <GlassActionRow
              v-for="doc in documents"
              :key="doc.href"
              class="settings-doc"
              :show-chevron="false"
              @click="openDocument(doc.href)"
            >
              <div class="settings-doc__text">
                <span class="settings-doc__title">{{ doc.title }}</span>
                <span class="settings-doc__link">Посмотреть документ</span>
              </div>
            </GlassActionRow>
          </div>
        </section>

        <div class="settings__operator">
          <div class="settings__komit-wrap">
            <img class="settings__komit" src="/client/icons/logo-komit.png" alt="КОМИТ" />
          </div>
          <section class="settings__requisites" aria-labelledby="settings-requisites-title">
            <h2 class="settings__requisites-title" id="settings-requisites-title">
              Реквизиты оператора
            </h2>
            <p>Сокращенное наименование: ООО «КОМИТ»</p>
            <p>ИНН: 1686059159</p>
            <p>
              Email:
              <a href="mailto:kom1t-digital@yandex.ru">kom1t-digital@yandex.ru</a>
            </p>
            <p>
              Контакты:
              <a href="tel:+79270319114">+7 (927) 031-91-14</a>
            </p>
          </section>
        </div>
      </template>
    </div>

    <HomeTabs :model-value="tab" @update:model-value="goToHomeTab" />

    <SuccessModal
      v-model="successOpen"
      title="Данные успешно изменены!"
      @continue="onSuccessContinue"
    />
  </q-page>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import GlassActionRow from '@/components/booking/GlassActionRow.vue'
import HomeTabs from '@/components/home/HomeTabs.vue'
import ClientHeader from '@/components/layout/ClientHeader.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseSwitcher from '@/components/ui/BaseSwitcher.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const tab = ''
const isEditing = ref(false)
const saving = ref(false)
const successOpen = ref(false)
const logoutLoading = ref(false)

const form = reactive({
  name: '',
  phone: '',
  email: ''
})

const consents = reactive({
  marketing: false,
  transfer: false,
  vk: false,
  telegram: false,
  max: false
})

const displayPhone = computed(() => form.phone?.trim() || '+7 999 999 99 99')
const displayEmail = computed(() => form.email?.trim() || 'pochta@mail.ru')

const consentItems = computed(() => [
  {
    key: 'marketing',
    title: 'Согласие на рассылки',
    description: `На почту ${displayEmail.value} будут приходить уведомления и рекламные материалы.`
  },
  {
    key: 'transfer',
    title: 'Согласие на передачу данных',
    description: 'Согласие на передачу данных вашего аккаунта и автомобиля при записи в автосервис.'
  },
  {
    key: 'vk',
    title: 'Уведомления VK',
    description: `Бот сможет отправлять аккаунту по номеру ${displayPhone.value} уведомления в ВК.`
  },
  {
    key: 'telegram',
    title: 'Уведомления Telegram',
    description: `Бот сможет отправлять аккаунту по номеру ${displayPhone.value} уведомления в Telegram.`
  },
  {
    key: 'max',
    title: 'Уведомления Max',
    description: `Бот сможет отправлять аккаунту по номеру ${displayPhone.value} уведомления в Мах.`
  }
])

const documents = [
  {
    title: 'Пользовательское соглашение',
    href: '/docs/user-agreement.html'
  },
  {
    title: 'Политика обработки персональных данных',
    href: '/docs/privacy-policy.html'
  },
  {
    title: 'Политика Cookies',
    href: '/docs/cookies-policy.html'
  }
]

function syncFormFromUser() {
  form.name = user.value?.name || ''
  form.phone = user.value?.phone || ''
  form.email = user.value?.email || ''
}

watch(user, syncFormFromUser, { immediate: true, deep: true })

function goToHomeTab(name) {
  router.push({ name: 'home', query: { tab: name } })
}

function startEdit() {
  syncFormFromUser()
  isEditing.value = true
}

function cancelEdit() {
  syncFormFromUser()
  isEditing.value = false
}

async function onSave() {
  if (saving.value) return
  saving.value = true
  try {
    await authStore.updateProfile({
      name: form.name.trim(),
      phone: form.phone,
      email: form.email.trim()
    })
    successOpen.value = true
  } finally {
    saving.value = false
  }
}

function onSuccessContinue() {
  successOpen.value = false
  isEditing.value = false
  syncFormFromUser()
}

function openDocument(href) {
  window.open(href, '_blank', 'noopener,noreferrer')
}

async function onLogout() {
  if (logoutLoading.value) return
  logoutLoading.value = true
  try {
    await authStore.logout()
  } finally {
    logoutLoading.value = false
    await router.replace({ name: 'login' })
  }
}
</script>

<style scoped lang="scss">
@use '../css/glass' as glass;

.settings {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  overflow: auto;
}

.settings__body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
  overflow: auto;
}

.settings__edit {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.settings__section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.settings__section-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.settings__form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.settings__form--edit {
  gap: 25px;
}

.settings__fields {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.settings__list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.settings-consent {
  @include glass.glass-light;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 40px;
  width: 100%;
  padding: 10px 15px;
  border-radius: 10px;
  box-sizing: border-box;
}

.settings-consent__switch {
  flex-shrink: 0;
}

.settings-consent__text {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
  text-align: left;
}

.settings-consent__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.settings-consent__desc {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-bg-dark);
}

.settings__list :deep(.settings-doc) {
  padding: 15px;
}

.settings__logout {
  margin-top: 0;
  --btn-solid: #e52626;
  --btn-light: #e52626;
  --btn-accent: #e52626;
  --btn-accent-fill: #e52626;
}

.settings-doc :deep(.glass-action-row__main) {
  align-items: flex-start;
}

.settings-doc__text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  min-width: 0;
}

.settings-doc__title {
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.settings-doc__link {
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  color: var(--dvijok-blue-primary);
}

.settings__edit-link {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  align-self: flex-end;
  gap: 5px;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  color: var(--dvijok-blue-primary);
}

.settings__edit-icon {
  display: block;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: var(--dvijok-blue-primary);
  -webkit-mask: url('/client/icons/my-car/edit.svg') center / contain no-repeat;
  mask: url('/client/icons/my-car/edit.svg') center / contain no-repeat;
}

.settings__back {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  align-self: flex-start;
  gap: 5px;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  color: var(--dvijok-blue-primary);
}

.settings__operator {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  width: fit-content;
  max-width: 100%;
  margin-inline: auto;
  min-width: 0;
  box-sizing: border-box;
}

.settings__komit-wrap {
  flex: 0 0 auto;
  height: calc(15px + 15px + 4 * 15px);
  aspect-ratio: 198 / 216;
  overflow: hidden;
}

.settings__komit {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.settings__requisites {
  display: flex;
  flex-direction: column;
  gap: 0;
  flex: 0 1 auto;
  min-width: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.settings__requisites p {
  margin: 0;
}

.settings__requisites a {
  color: inherit;
  text-decoration: none;
}

.settings__requisites-title {
  margin: 0 0 15px;
  font-size: inherit;
  line-height: inherit;
  font-weight: 700;
  text-transform: uppercase;
  color: inherit;
}
</style>
