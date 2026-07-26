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
          <BaseField
            v-model="security.currentPassword"
            :type="showPassword ? 'text' : 'password'"
            label="Текущий пароль"
            :hint="passwordChangedHint"
            readonly
            class="account__password-field"
          >
            <template #append>
              <q-btn
                flat
                dense
                type="button"
                class="account__eye-btn"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showPassword = !showPassword"
              >
                <EyeIcon :closed="showPassword" />
              </q-btn>
            </template>
          </BaseField>
          <BaseButton text :icon-spacing="10">
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
              <span class="confirm-method__value">{{ security.email }}</span>
              <span class="confirm-method__hint">будет отправлено письмо подтверждения</span>
            </div>
            <BaseButton text :icon-spacing="10">
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
              <span class="confirm-method__value">{{ security.phone }}</span>
              <span class="confirm-method__hint">будет отправлено SMS-подтверждения</span>
            </div>
            <BaseButton text :icon-spacing="10">
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

        <div class="sessions-list">
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
        </div>
      </section>

      <section class="settings-card">
        <div class="settings-card__head">
          <h2 class="settings-card__title">Истории входов</h2>
          <BaseButton text :icon-spacing="10">
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
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseSwitcher from '@/components/ui/BaseSwitcher.vue'
import EyeIcon from '@/components/ui/EyeIcon.vue'
import Radio from '@/components/ui/Radio.vue'
import { formatDateTime, formatRuDateShort } from '@/utils/formatDateRu.js'

defineProps({
  serviceName: {
    type: String,
    default: ''
  }
})

const security = defineModel('security', { type: Object, required: true })
const emit = defineEmits(['logout'])

const showPassword = ref(false)

const sessions = computed(() => security.value.sessions || [])
const otherSessions = computed(() => sessions.value.filter(session => !session.current))
const loginHistory = computed(() => (security.value.loginHistory || []).slice(0, 3))

const passwordChangedHint = computed(() => {
  const date = formatRuDateShort(security.value.passwordChangedAt)
  return date ? `Последн. изм. ${date}` : ''
})

function terminateSession(id) {
  security.value.sessions = security.value.sessions.filter(session => session.id !== id)
}

function terminateAllSessions() {
  security.value.sessions = security.value.sessions.filter(session => session.current)
}
</script>

<style scoped lang="scss">
@use './settingsShared.scss';

.settings-card--gap-15 {
  gap: 15px;
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

.account__password-field {
  width: 300px;
}

.account__eye-btn {
  min-height: auto;
  padding: 0;
  pointer-events: auto;
  cursor: pointer;

  :deep(.q-btn__content) {
    padding: 0;
  }
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
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
