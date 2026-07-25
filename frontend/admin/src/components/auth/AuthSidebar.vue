<template>
  <aside class="auth-sidebar">
    <div class="auth-sidebar__rounds" aria-hidden="true">
      <img class="auth-sidebar__round auth-sidebar__round--1" src="/admin/round.svg" alt="" />
      <img class="auth-sidebar__round auth-sidebar__round--2" src="/admin/round.svg" alt="" />
    </div>

    <div class="auth-sidebar__block auth-sidebar__block--logo">
      <img class="auth-sidebar__logo" src="/admin/icons/auth/logo.svg" alt="DVIJOK" />
    </div>

    <div class="auth-sidebar__block auth-sidebar__block--welcome">
      <p v-if="isLogin" class="auth-sidebar__welcome-title">Добро пожаловать!</p>
      <p v-else class="auth-sidebar__welcome-title"> Начните работу<br />уже сегодня </p>
      <p v-if="isLogin" class="auth-sidebar__welcome-text">
        Войдите, чтобы управлять заказами и клиентами
      </p>
      <p v-else class="auth-sidebar__welcome-text">
        Управляйте заказами, клиентами<br />и мастерами в одном окне
      </p>
    </div>

    <div v-if="isLogin" class="auth-sidebar__block auth-sidebar__block--beta">
      <p class="auth-sidebar__beta-title">* Это бета-тест</p>
      <p class="auth-sidebar__beta-text">
        Команда «Комит» рада представить новый сервис<br />
        для оптимизации работы автомастерских — CRM-систему «Движок»
      </p>
    </div>

    <ul v-else class="auth-sidebar__block auth-sidebar__features">
      <li class="auth-sidebar__feature">
        <img class="auth-sidebar__feature-icon" src="/admin/icons/auth/canban.svg" alt="" />
        <div class="auth-sidebar__feature-body">
          <p class="auth-sidebar__feature-title">Канбан-доска заказов</p>
          <p class="auth-sidebar__feature-text">Все заказы в одном месте</p>
        </div>
      </li>
      <li class="auth-sidebar__feature">
        <img class="auth-sidebar__feature-icon" src="/admin/icons/auth/crm.svg" alt="" />
        <div class="auth-sidebar__feature-body">
          <p class="auth-sidebar__feature-title">CRM для клиентов</p>
          <p class="auth-sidebar__feature-text">История и контакты всегда под рукой</p>
        </div>
      </li>
      <li class="auth-sidebar__feature">
        <img class="auth-sidebar__feature-icon" src="/admin/icons/auth/docs.svg" alt="" />
        <div class="auth-sidebar__feature-body">
          <p class="auth-sidebar__feature-title">Аналитика и отчеты</p>
          <p class="auth-sidebar__feature-text">Выручка, загрузка, эффективность</p>
        </div>
      </li>
      <li class="auth-sidebar__feature">
        <img class="auth-sidebar__feature-icon" src="/admin/icons/auth/calendar.svg" alt="" />
        <div class="auth-sidebar__feature-body">
          <p class="auth-sidebar__feature-title">Расписание мастеров</p>
          <p class="auth-sidebar__feature-text">Планирование и учет рабочего времени</p>
        </div>
      </li>
    </ul>

    <div class="auth-sidebar__block auth-sidebar__block--register">
      <p v-if="isLogin" class="auth-sidebar__register-text">Еще нет аккаунта?</p>
      <p v-else class="auth-sidebar__register-text">Уже зарегистрированы?</p>
      <div class="auth-sidebar__register-link" @click="$emit('toggle')">
        <span class="auth-sidebar__register-action">
          {{ isLogin ? 'Зарегистрировать автосервис' : 'Войти в систему' }}
        </span>
        <ArrowIcon
          class="auth-sidebar__register-arrow"
          direction="right"
          color="var(--dvijok-white)"
        />
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'login',
    validator: value => ['login', 'register'].includes(value)
  }
})

defineEmits(['toggle'])

const isLogin = computed(() => props.mode === 'login')
</script>

<style scoped lang="scss">
.auth-sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 60px;
  width: 446px;
  flex-shrink: 0;
  padding: 20px;
  background-color: var(--dvijok-bg-dark);
  overflow: hidden;
}

.auth-sidebar__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.auth-sidebar__round {
  position: absolute;
  pointer-events: none;
  width: auto;
  height: auto;
  object-fit: contain;
}

.auth-sidebar__round--1 {
  width: 412px;
  height: 412px;
  top: 0;
  right: 0;
  transform: translate(45%, -25%);
  z-index: 0;
}

.auth-sidebar__round--2 {
  width: 389px;
  height: 389px;
  bottom: 0;
  left: 0;
  transform: translate(-20%, 50%);
  z-index: 0;
}

.auth-sidebar__block {
  position: relative;
  z-index: 1;
  width: 100%;
}

.auth-sidebar__logo {
  display: block;
  max-width: 100%;
  height: auto;
}

.auth-sidebar__block--welcome {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-sidebar__welcome-title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 20px;
  font-weight: 600;
  line-height: 30px;
}

.auth-sidebar__welcome-text {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
}

.auth-sidebar__block--beta {
  padding: 10px 30px;
  background-image: url('/admin/icons/auth/background.svg');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.auth-sidebar__beta-title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.auth-sidebar__beta-text {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 9px;
  font-weight: 400;
  line-height: 11px;
}

.auth-sidebar__block--register {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-sidebar__register-text {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
}

.auth-sidebar__register-link {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.auth-sidebar__register-action {
  color: var(--dvijok-white);
  font-size: 14px;
  font-weight: 600;
  line-height: 17px;
  text-decoration: underline;
}

.auth-sidebar__register-arrow {
  display: block;
}

.auth-sidebar__features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.auth-sidebar__feature {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  padding: 10px 30px;
  background-image: url('/admin/icons/auth/background.svg');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.auth-sidebar__feature-icon {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.auth-sidebar__feature-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.auth-sidebar__feature-title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.auth-sidebar__feature-text {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 12px;
  font-weight: 400;
  line-height: 15px;
}
</style>
