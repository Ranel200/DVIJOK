<template>
  <q-page class="tariffs" :class="{ 'tariffs--checkout': isCheckout }">
    <!-- Выбор тарифа -->
    <template v-if="!isCheckout">
      <section class="tariffs__select">
        <img class="tariffs__round" src="/admin/round.svg" alt="" aria-hidden="true" />

        <div class="tariffs__content">
          <img class="tariffs__logo" src="/admin/icons/logo.svg" alt="DVIJOK" />

          <div class="tariffs__heading">
            <h1 class="tariffs__title">Тарифы для вашего сервиса</h1>
            <p class="tariffs__subtitle">
              Выберите нужный вам тариф и оформите подписку.<br />
              Первый месяц бесплатно всем новым пользователям!
            </p>
          </div>

          <div class="tariffs__cards">
            <article v-for="plan in plans" :key="plan.id" class="tariff-card">
              <div class="tariff-card__top">
                <img class="tariff-card__logo" :src="plan.logo" :alt="plan.logoAlt" />
                <div class="tariff-card__text">
                  <p class="tariff-card__summary">{{ plan.summary }}</p>
                  <p class="tariff-card__description">{{ plan.description }}</p>
                </div>
              </div>

              <p class="tariff-card__price">{{ plan.price }}</p>

              <BaseButton
                color="blue1"
                scheme="outlinedWhite-solid-outlinedWhite"
                size="lg"
                block
                @click="goToCheckout(plan)"
              >
                Оформить тариф
              </BaseButton>
            </article>
          </div>
        </div>

        <p class="tariffs__support tariffs__support--select">
          Техподдержка: support@dvijok.ru · 8 800 000-00-00
        </p>
      </section>
    </template>

    <!-- Оформление выбранного тарифа -->
    <template v-else>
      <TariffSidebar :plan="selectedPlan" />

      <section class="tariffs__checkout">
        <div class="tariffs__checkout-card">
          <div class="tariffs__checkout-heading">
            <h1 class="tariffs__checkout-title">Оплата тарифа {{ selectedPlan.name }}</h1>
            <p class="tariffs__checkout-subtitle">Введите данные для платежа</p>
          </div>

          <BaseField
            v-model="form.phone"
            class="tariffs__field"
            label="Телефон"
            placeholder="Укажите ваш телефон"
            block
          />

          <BaseField
            v-model="form.email"
            class="tariffs__field"
            label="Почта"
            placeholder="Укажите вашу почту"
            block
          />

          <div class="tariffs__remember">
            <BaseCheckbox v-model="form.remember" />
            <BaseButton color="blue1" text @click="form.remember = !form.remember">
              Запомнить реквизиты
            </BaseButton>
          </div>

          <div class="tariffs__pay-actions">
            <BaseButton
              color="blue1"
              scheme="solid-light-outlined"
              size="lg"
              block
              :loading="paying === 'bank'"
              :disable="Boolean(paying)"
              @click="requestPay('bank')"
            >
              Оплатить {{ selectedPlan.price }} через банковский счет
            </BaseButton>

            <div class="tariffs__or" aria-hidden="true">
              <span class="tariffs__or-line" />
              <span class="tariffs__or-text">или</span>
              <span class="tariffs__or-line" />
            </div>

            <BaseButton
              class="tariffs__sbp-btn"
              color="blue1"
              scheme="outlinedWhite-solid-outlinedWhite"
              size="lg"
              block
              :loading="paying === 'sbp'"
              :disable="Boolean(paying)"
              @click="requestPay('sbp')"
            >
              <template #prepend>
                <img class="tariffs__sbp-icon" src="/admin/icons/tariffs/sbp.png" alt="" />
              </template>
              Оплатить {{ selectedPlan.price }} через СБП
            </BaseButton>
          </div>
        </div>

        <p class="tariffs__support">Техподдержка: support@dvijok.ru · 8 800 000-00-00</p>
      </section>

      <BaseModal v-model="confirmOpen" persistent>
        <div class="tariffs__success">
          <p class="tariffs__confirm-text">
            Оплачивая подписку, вы подтверждаете, что ознакомились и принимаете условия
            <a
              class="tariffs__confirm-link"
              :href="offerDocument.href"
              target="_blank"
              rel="noopener noreferrer"
              >Договора оферты</a
            >
            и
            <a
              class="tariffs__confirm-link"
              :href="licenseDocument.href"
              target="_blank"
              rel="noopener noreferrer"
              >Лицензионного договора</a
            >
          </p>
          <BaseButton
            color="blue1"
            scheme="solid-light-outlined"
            size="lg"
            :loading="Boolean(paying)"
            @click="confirmPay"
          >
            Все верно
          </BaseButton>
        </div>
      </BaseModal>

      <BaseModal v-model="success" persistent>
        <div class="tariffs__success">
          <h2 class="tariffs__success-title">
            Оплата тарифа {{ selectedPlan.name }} прошла успешно!
          </h2>
          <BaseButton color="blue1" scheme="solid-light-outlined" size="lg" @click="goToSystem">
            Перейти в систему
          </BaseButton>
        </div>
      </BaseModal>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import TariffSidebar from '@/components/auth/TariffSidebar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { PLATFORM_DOCUMENTS } from '@/constants/platformDocuments.js'
import { tariffsApi } from '@/api/index.js'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const offerDocument = PLATFORM_DOCUMENTS.find(doc => doc.id === 'offer')
const licenseDocument = PLATFORM_DOCUMENTS.find(doc => doc.id === 'license')

const plans = ref([])
const selectedPlan = ref(null)
const paying = ref(null)
const pendingMethod = ref(null)
const confirmOpen = ref(false)
const success = ref(false)

const form = reactive({
  phone: '',
  email: '',
  remember: false
})

const isCheckout = computed(() => Boolean(selectedPlan.value))

onMounted(async () => {
  plans.value = await tariffsApi.list()
})

function goToCheckout(plan) {
  selectedPlan.value = plan
}

function requestPay(method) {
  if (paying.value || !selectedPlan.value) return
  pendingMethod.value = method
  confirmOpen.value = true
}

async function confirmPay() {
  if (paying.value || !selectedPlan.value || !pendingMethod.value) return
  paying.value = pendingMethod.value
  try {
    await authStore.selectSubscriptionPlan(selectedPlan.value.id)
    confirmOpen.value = false
    pendingMethod.value = null
    success.value = true
  } finally {
    paying.value = null
  }
}

function goToSystem() {
  success.value = false
  router.push(authStore.homeRoute)
}
</script>

<style scoped lang="scss">
.tariffs {
  display: flex;
  min-height: 100vh;
}

.tariffs--checkout {
  background-color: var(--dvijok-muted);
}

.tariffs__select {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: var(--dvijok-bg-dark);
}

.tariffs__round {
  position: absolute;
  top: 0;
  right: 0;
  width: 40vw;
  height: auto;
  pointer-events: none;
  transform: translate(-25%, -75%);
  z-index: 0;
}

.tariffs__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 1280px;
  padding: 50px 75px;
}

.tariffs__logo {
  display: block;
  width: min(280px, 40%);
  height: auto;
}

.tariffs__heading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tariffs__title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 24px;
  font-weight: 600;
  line-height: 36px;
}

.tariffs__subtitle {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 16px;
  font-weight: 400;
  line-height: 19px;
}

.tariffs__cards {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 20px;
  width: 100%;
}

.tariff-card {
  position: relative;
  isolation: isolate;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
  padding: 30px;
  overflow: hidden;
  border-radius: 15px;
  background-color: transparent;
  background-image: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.14) 0%,
    rgba(255, 255, 255, 0.05) 35%,
    rgba(255, 255, 255, 0.02) 65%,
    rgba(255, 255, 255, 0.08) 100%
  );
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.tariff-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0) 22%,
    rgba(255, 255, 255, 0) 78%,
    rgba(255, 255, 255, 0.35) 100%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.tariff-card__top {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0;
}

.tariff-card__logo {
  display: block;
  width: 100%;
  max-width: 315px;
  height: auto;
}

.tariff-card__text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tariff-card__summary {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 13px;
  font-weight: 700;
  line-height: normal;
}

.tariff-card__description {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 13px;
  font-weight: 400;
  line-height: normal;
}

.tariff-card__price {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 36px;
  font-weight: 600;
  line-height: normal;
}

.tariffs__checkout {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.tariffs__checkout-card {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
  max-width: 681px;
  padding: 75px;
  background-color: var(--dvijok-white);
  border-radius: 15px;
}

.tariffs__checkout-heading {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tariffs__checkout-title {
  margin: 0;
  color: var(--dvijok-text-heading);
  font-size: 32px;
  font-weight: 700;
  line-height: normal;
  text-align: center;
}

.tariffs__checkout-subtitle {
  margin: 0;
  color: var(--dvijok-text-secondary);
  font-size: 16px;
  font-weight: 400;
  line-height: normal;
  text-align: center;
}

.tariffs__field {
  width: 100%;
}

.tariffs__remember {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.tariffs__pay-actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
}

.tariffs__or {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 100%;
}

.tariffs__or-line {
  flex: 1;
  height: 1px;
  background-color: var(--dvijok-text-secondary);
  opacity: 0.4;
}

.tariffs__or-text {
  color: var(--dvijok-text-secondary);
  font-size: 16px;
  font-weight: 400;
  line-height: 19px;
}

.tariffs__sbp-icon {
  display: block;
  width: 50px;
  height: 23px;
  object-fit: contain;
}

.tariffs__sbp-btn.base-btn {
  &:not(:disabled):not(.q-btn--disabled):hover {
    color: var(--dvijok-white) !important;
    background: #7a82a0 !important;
    box-shadow: inset 0 0 0 2px #7a82a0 !important;
  }

  &:not(:disabled):not(.q-btn--disabled):active {
    color: var(--dvijok-link-hover) !important;
    background: rgb(255 255 255 / 10%) !important;
    box-shadow: inset 0 0 0 2px #7a82a0 !important;
  }
}

.tariffs__support {
  position: absolute;
  bottom: 20px;
  z-index: 1;
  margin: 0;
  color: var(--dvijok-text-tertiary);
  font-size: 11px;
  font-weight: 500;
  line-height: 13px;
}

.tariffs__support--select {
  color: var(--dvijok-muted);
}

.tariffs__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  padding: 20px;
  text-align: center;
}

.tariffs__success-title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
}

.tariffs__confirm-text {
  margin: 0;
  max-width: 520px;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
}

.tariffs__confirm-link {
  color: var(--dvijok-blue-deep);
  text-decoration: underline;
}
</style>
