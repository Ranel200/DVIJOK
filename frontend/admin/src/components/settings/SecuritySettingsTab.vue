<template>
  <div class="settings">
    <div class="settings__col">
      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Аккаунт</h2>
          <BaseButton color="red" text @click="emit('logout')">Выйти из аккаунта</BaseButton>
        </div>

        <div class="account__name">{{ serviceName }}</div>

        <div class="account__password">
          <div class="account__security-level">
            <span class="account__security-level-label">Текущий уровень безопасности</span>
            <div class="account__security-level-control">
              <div class="account__security-level-row">
                <div
                  class="account__security-progress"
                  :style="{ backgroundColor: securityLevelMeta.bg }"
                >
                  <div
                    class="account__security-progress-fill"
                    :style="{
                      width: securityLevelMeta.width,
                      backgroundColor: securityLevelMeta.color
                    }"
                  />
                </div>
                <span
                  class="account__security-pill"
                  :style="{
                    color: securityLevelMeta.color,
                    backgroundColor: securityLevelMeta.bg
                  }"
                >
                  {{ securityLevelMeta.label }}
                </span>
              </div>
              <p v-if="passwordChangedHint" class="account__security-hint">
                {{ passwordChangedHint }}
              </p>
            </div>
          </div>
          <BaseButton text :icon-spacing="10" @click="openPasswordEdit">
            Изменить пароль
            <template #append>
              <ArrowIcon direction="right" :size="14" />
            </template>
          </BaseButton>
        </div>
      </section>

      <section class="settings-card settings-card--gap-15">
        <h2 class="settings-card__title">Подтверждение входа</h2>

        <div class="confirm-method">
          <div class="confirm-method__head">
            <span class="confirm-method__title">Подтверждение на почту</span>
            <BaseSwitcher
              v-model="security.emailConfirmEnabled"
              aria-label="Подтверждение на почту"
            />
          </div>
          <div class="confirm-method__body">
            <div class="confirm-method__info">
              <span class="confirm-method__hint">При каждом входе на почту</span>
              <span class="confirm-method__value">{{ email }}</span>
              <span class="confirm-method__hint">будет отправлено письмо подтверждения</span>
            </div>
            <BaseButton text :icon-spacing="10" @click="emit('edit-service', 'email')">
              Изменить почту
              <template #append>
                <ArrowIcon direction="right" :size="14" />
              </template>
            </BaseButton>
          </div>
        </div>

        <div class="confirm-method">
          <div class="confirm-method__head">
            <span class="confirm-method__title">Подтверждение на номер телефона</span>
            <BaseSwitcher
              v-model="security.phoneConfirmEnabled"
              aria-label="Подтверждение на номер телефона"
            />
          </div>
          <div class="confirm-method__body">
            <div class="confirm-method__info">
              <span class="confirm-method__hint">При каждом входе на номер</span>
              <span class="confirm-method__value">{{ phone }}</span>
              <span class="confirm-method__hint">будет отправлено SMS-подтверждения</span>
            </div>
            <BaseButton text :icon-spacing="10" @click="emit('edit-service', 'phone')">
              Изменить номер
              <template #append>
                <ArrowIcon direction="right" :size="14" />
              </template>
            </BaseButton>
          </div>
        </div>
      </section>
    </div>

    <div class="settings__col">
      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Активные сессии</h2>
          <BaseButton
            color="red"
            text
            :disable="otherSessions.length === 0"
            @click="terminateAllSessions"
          >
            Завершить все
          </BaseButton>
        </div>

        <TransitionGroup name="session" tag="div" class="sessions-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            :class="['session-item', { 'session-item--active': session.current }]"
          >
            <div class="session-item__left">
              <div class="session-item__icon">
                <img :src="`/admin/icons/settings/${session.type}.svg`" alt="" />
              </div>
              <div class="session-item__info">
                <span class="session-item__title">
                  {{ session.deviceName }} — {{ session.browser }}
                </span>
                <span class="session-item__meta">
                  {{ session.city }}, {{ session.country }} · {{ session.ip }}
                </span>
                <span class="session-item__time">{{ formatDateTime(session.lastActiveAt) }}</span>
              </div>
            </div>

            <div class="session-item__right">
              <div v-if="session.current" class="session-item__pill">
                <Radio filled color="#157848" :size="12" />
                <span>Активен</span>
              </div>
              <BaseButton v-else color="red" text @click="terminateSession(session.id)">
                Завершить
              </BaseButton>
            </div>
          </div>
        </TransitionGroup>
      </section>

      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Истории входов</h2>
          <BaseButton text :icon-spacing="10" @click="loginHistoryOpen = true">
            Посмотреть все
            <template #append>
              <ArrowIcon direction="right" :size="14" />
            </template>
          </BaseButton>
        </div>

        <div class="login-history">
          <div v-for="entry in loginHistory" :key="entry.id" class="login-history__item">
            <div class="login-history__left">
              <div class="login-history__status-wrap">
                <span
                  class="login-history__status"
                  :style="{ background: entry.success ? '#157848' : '#EF0A0A' }"
                />
              </div>
              <div class="login-history__info">
                <span class="session-item__title">
                  {{ entry.deviceName }} — {{ entry.browser }}
                </span>
                <span class="session-item__meta">
                  {{ entry.city }}, {{ entry.country }} · {{ entry.ip }} ·
                  {{ entry.success ? 'Успешно' : 'Неудачная попытка' }}
                </span>
              </div>
            </div>
            <span class="login-history__time">{{ formatDateTime(entry.loggedAt) }}</span>
          </div>
        </div>
      </section>
    </div>

    <BaseModal v-model="passwordEditOpen" fit hide-close>
      <div class="password-edit">
        <h2 class="password-edit__title">Изменение пароля</h2>
        <div class="password-edit__body">
          <BaseField
            v-model="passwordDraft.oldPassword"
            :type="visible.old ? 'text' : 'password'"
            label="Введите старый пароль"
            placeholder="Пароль"
            :error="Boolean(passwordErrors.oldPassword)"
            :error-message="passwordErrors.oldPassword"
            block
          >
            <template #append>
              <q-btn
                flat
                dense
                type="button"
                class="password-edit__eye"
                :aria-label="visible.old ? 'Скрыть пароль' : 'Показать пароль'"
                @click="visible.old = !visible.old"
              >
                <EyeIcon :closed="visible.old" />
              </q-btn>
            </template>
          </BaseField>

          <div class="password-edit__new">
            <BaseField
              v-model="passwordDraft.newPassword"
              :type="visible.next ? 'text' : 'password'"
              label="Придумайте новый пароль"
              placeholder="Пароль"
              :error="Boolean(passwordErrors.newPassword)"
              :error-message="passwordErrors.newPassword"
              block
            >
              <template #append>
                <q-btn
                  flat
                  dense
                  type="button"
                  class="password-edit__eye"
                  :aria-label="visible.next ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="visible.next = !visible.next"
                >
                  <EyeIcon :closed="visible.next" />
                </q-btn>
              </template>
            </BaseField>
            <BaseField
              v-model="passwordDraft.confirmPassword"
              :type="visible.confirm ? 'text' : 'password'"
              label="Повторите новый пароль"
              placeholder="Пароль"
              :error="Boolean(passwordErrors.confirmPassword)"
              :error-message="passwordErrors.confirmPassword"
              block
            >
              <template #append>
                <q-btn
                  flat
                  dense
                  type="button"
                  class="password-edit__eye"
                  :aria-label="visible.confirm ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="visible.confirm = !visible.confirm"
                >
                  <EyeIcon :closed="visible.confirm" />
                </q-btn>
              </template>
            </BaseField>
          </div>

          <div class="password-edit__code-block">
            <div class="password-edit__send-wrap">
              <BaseButton
                color="blue1"
                size="lg"
                class="password-edit__send"
                :loading="codeSending"
                @click="sendCode"
              >
                Отправить код
              </BaseButton>
              <p class="password-edit__hint">
                *Код подтверждения смены пароля придет на почту {{ email }}
              </p>
            </div>
            <div class="password-edit__code">
              <span class="password-edit__code-label">Код подтверждения</span>
              <CodeInputs v-model="passwordDraft.code" :error="Boolean(passwordErrors.code)" />
              <p v-if="passwordErrors.code" class="password-edit__code-error">
                {{ passwordErrors.code }}
              </p>
            </div>
          </div>
        </div>
      </div>
      <template #actions>
        <div class="password-edit__actions">
          <BaseButton
            color="blue1"
            scheme="outlinedWhite-solid-outlinedWhite"
            size="lg"
            @click="passwordEditOpen = false"
          >
            Отмена
          </BaseButton>
          <BaseButton color="green" size="lg" :loading="passwordSaving" @click="savePassword">
            Сохранить изменения
          </BaseButton>
        </div>
      </template>
    </BaseModal>

    <BaseModal v-model="loginHistoryOpen" fit @show="onLoginHistoryShow">
      <div class="login-history-modal">
        <h2 class="login-history-modal__title">Истории входов за последний год</h2>
        <BaseScrollbar
          ref="historyScrollbarRef"
          class="login-history-modal__body"
          content-class="login-history-modal__scroll"
        >
          <div v-for="entry in allLoginHistory" :key="entry.id" class="login-history__item">
            <div class="login-history__left">
              <div class="login-history__status-wrap">
                <span
                  class="login-history__status"
                  :style="{ background: entry.success ? '#157848' : '#EF0A0A' }"
                />
              </div>
              <div class="login-history__info">
                <span class="session-item__title">
                  {{ entry.deviceName }} — {{ entry.browser }}
                </span>
                <span class="session-item__meta">
                  {{ entry.city }}, {{ entry.country }} · {{ entry.ip }} ·
                  {{ entry.success ? 'Успешно' : 'Неудачная попытка' }}
                </span>
              </div>
            </div>
            <span class="login-history__time">{{ formatDateTime(entry.loggedAt) }}</span>
          </div>
        </BaseScrollbar>
      </div>
    </BaseModal>

    <SuccessModal v-model="passwordSavedOpen" message="Пароль сохранен!" />
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import CodeInputs from '@/components/ui/CodeInputs.vue'
import BaseScrollbar from '@/components/ui/BaseScrollbar.vue'
import BaseSwitcher from '@/components/ui/BaseSwitcher.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import Radio from '@/components/ui/Radio.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import { authApi, settingsApi } from '@/api/index.js'
import { formatDateTime, formatRuDateShort } from '@/utils/formatDateRu.js'

const props = defineProps({
  serviceName: {
    type: String,
    default: ''
  },
  email: {
    type: String,
    default: ''
  },
  phone: {
    type: String,
    default: ''
  }
})

const SECURITY_LEVELS = {
  veryReliable: {
    label: 'Очень надёжно',
    width: '95%',
    color: '#157848',
    bg: '#D5F0E4'
  },
  reliable: {
    label: 'Надёжно',
    width: '82%',
    color: '#8AC820',
    bg: '#E9FFC4'
  },
  medium: {
    label: 'Не очень надёжно',
    width: '50%',
    color: '#F06D30',
    bg: '#F0E4D5'
  },
  weak: {
    label: 'Слабая защита',
    width: '28%',
    color: '#B60000',
    bg: '#F0D5D5'
  }
}

const security = defineModel('security', { type: Object, required: true })
const emit = defineEmits(['logout', 'edit-service'])

const passwordEditOpen = ref(false)
const passwordSavedOpen = ref(false)
const passwordSaving = ref(false)
const codeSending = ref(false)
const codeSent = ref(false)
const loginHistoryOpen = ref(false)
const historyScrollbarRef = ref(null)
const visible = reactive({ old: false, next: false, confirm: false })
const passwordDraft = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
  code: ''
})
const passwordErrors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
  code: ''
})

const sessions = computed(() => security.value.sessions || [])
const otherSessions = computed(() => sessions.value.filter(session => !session.current))
const allLoginHistory = computed(() => security.value.loginHistory || [])
const loginHistory = computed(() => allLoginHistory.value.slice(0, 3))

const securityLevelMeta = computed(
  () => SECURITY_LEVELS[security.value.securityLevel] || SECURITY_LEVELS.medium
)

const passwordChangedHint = computed(() => {
  const date = formatRuDateShort(security.value.passwordChangedAt)
  return date ? `Последн. изм. ${date}` : ''
})

function onLoginHistoryShow() {
  nextTick(() => historyScrollbarRef.value?.update())
}

function clearPasswordErrors() {
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
  passwordErrors.code = ''
}

function openPasswordEdit() {
  passwordDraft.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    code: ''
  }
  clearPasswordErrors()
  codeSent.value = false
  visible.old = false
  visible.next = false
  visible.confirm = false
  passwordEditOpen.value = true
}

function validatePasswordDraft() {
  clearPasswordErrors()
  const draft = passwordDraft.value
  let valid = true

  if (!draft.oldPassword.trim()) {
    passwordErrors.oldPassword = 'Введите старый пароль'
    valid = false
  }

  if (!draft.newPassword.trim()) {
    passwordErrors.newPassword = 'Введите новый пароль'
    valid = false
  } else if (draft.newPassword === draft.oldPassword) {
    passwordErrors.newPassword = 'Новый пароль должен отличаться от старого'
    valid = false
  }

  if (!draft.confirmPassword.trim()) {
    passwordErrors.confirmPassword = 'Повторите новый пароль'
    valid = false
  } else if (draft.confirmPassword !== draft.newPassword) {
    passwordErrors.confirmPassword = 'Пароли не совпадают'
    valid = false
  }

  if (!codeSent.value) {
    passwordErrors.code = 'Сначала отправьте код подтверждения'
    valid = false
  } else if (draft.code.replace(/\D/g, '').length < 4) {
    passwordErrors.code = 'Введите код подтверждения'
    valid = false
  }

  return valid
}

async function sendCode() {
  codeSending.value = true
  try {
    await settingsApi.update({ action: 'sendPasswordCode', email: props.email })
    codeSent.value = true
    passwordErrors.code = ''
  } finally {
    codeSending.value = false
  }
}

async function savePassword() {
  if (!validatePasswordDraft()) return

  passwordSaving.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const updated = await settingsApi.update({
      security: {
        currentPassword: passwordDraft.value.newPassword,
        passwordChangedAt: today,
        oldPassword: passwordDraft.value.oldPassword,
        code: passwordDraft.value.code
      }
    })
    if (updated?.security) {
      security.value = { ...security.value, ...updated.security }
    }
    passwordEditOpen.value = false
    passwordSavedOpen.value = true
  } catch (err) {
    const detail = err?.data?.detail
    const message =
      err?.data?.message ||
      (typeof detail === 'string' ? detail : detail?.message) ||
      'Не удалось изменить пароль'
    if (err?.status === 401) passwordErrors.oldPassword = message
    else passwordErrors.newPassword = message
  } finally {
    passwordSaving.value = false
  }
}

async function terminateSession(id) {
  await authApi.revokeSession(id)
  security.value.sessions = security.value.sessions.filter(session => session.id !== id)
}

async function terminateAllSessions() {
  await authApi.revokeOtherSessions()
  security.value.sessions = security.value.sessions.filter(session => session.current)
}
</script>

<style scoped lang="scss">
@use './settingsShared.scss';

.settings-card--gap-15 {
  gap: 15px;
}

.password-edit {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.password-edit__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 16px;
  font-weight: 600;
  line-height: 19px;
  text-transform: uppercase;
}

.password-edit__body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.password-edit__new {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.password-edit__code-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.password-edit__send-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.password-edit__send {
  width: fit-content;
}

.password-edit__hint {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.password-edit__code {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.password-edit__code-label {
  color: var(--dvijok-form-label, var(--dvijok-bg-dark));
  font-size: 16px;
  line-height: 19px;
  text-align: left;
  white-space: nowrap;
}

.password-edit__code-error {
  margin: 0;
  color: var(--q-negative, #c10015);
  font-size: 12px;
  line-height: 15px;
}

.password-edit__eye {
  min-height: auto;
  padding: 0;
  pointer-events: auto;
  cursor: pointer;

  :deep(.q-btn__content) {
    padding: 0;
  }
}

.password-edit__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.account__name {
  color: var(--dvijok-bg-dark);
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
}

.account__password {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.account__security-level {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.account__security-level-label {
  color: var(--dvijok-form-label, var(--dvijok-text-secondary));
  font-size: 14px;
  line-height: 16px;
  text-align: left;
  white-space: nowrap;
}

.account__security-level-control {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
  min-width: 0;
}

.account__security-level-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.account__security-progress {
  width: 70%;
  height: 6px;
  border-radius: 50px;
  overflow: hidden;
  flex-shrink: 0;
}

.account__security-progress-fill {
  height: 100%;
  border-radius: 50px;
}

.account__security-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 50px;
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

.account__security-hint {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.confirm-method {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 0;
}

.confirm-method__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.confirm-method__title {
  color: var(--dvijok-text-primary);
  font-weight: 700;
  font-size: 15px;
  line-height: 18px;
}

.confirm-method__body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.confirm-method__info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.confirm-method__hint {
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.confirm-method__value {
  color: var(--dvijok-text-primary);
  font-weight: 700;
  font-size: 15px;
  line-height: 18px;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  max-height: calc(3 * 77px);
  overflow-y: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.session-item {
  box-sizing: border-box;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
}

.session-leave-active {
  overflow: hidden;
  transition:
    max-height 0.28s ease,
    padding 0.28s ease,
    opacity 0.2s ease;
  max-height: 77px;
}

.session-leave-to {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
}

.session-item--active {
  padding: 9px;
  border: 1px solid #093095;
  background: #ccdaff;
}

.session-item__left {
  display: flex;
  align-items: center;
  gap: 30px;
  min-width: 0;
}

.session-item__icon {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 50px;
  height: 31px;
  flex-shrink: 0;
}

.session-item__icon img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.session-item__info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.session-item__title {
  color: var(--dvijok-text-primary);
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
}

.session-item__meta {
  color: var(--dvijok-text-secondary);
  font-weight: 600;
  font-size: 12px;
  line-height: 15px;
}

.session-item__time {
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
}

.session-item__right {
  flex-shrink: 0;
}

.session-item__pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border: 1px solid #157848;
  border-radius: 50px;
  background: #d5f0e4;
  color: #157848;
  font-size: 10px;
  font-weight: 600;
  line-height: 12px;
  white-space: nowrap;
}

.login-history {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.login-history-modal {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  min-height: 0;
}

.login-history-modal__title {
  margin: 0;
  padding-right: 36px;
  color: var(--dvijok-bg-dark);
  font-size: 16px;
  font-weight: 600;
  line-height: 19px;
  text-transform: uppercase;
}

.login-history-modal__body {
  max-height: 420px;
}

.login-history-modal__body :deep(.login-history-modal__scroll) {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.login-history__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
}

.login-history__left {
  display: flex;
  align-items: center;
  gap: 30px;
  min-width: 0;
}

.login-history__status-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 50px;
  height: 17px;
  flex-shrink: 0;
}

.login-history__status {
  display: block;
  width: 17px;
  height: 17px;
  border-radius: 50%;
}

.login-history__info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.login-history__time {
  flex-shrink: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  white-space: nowrap;
}
</style>
