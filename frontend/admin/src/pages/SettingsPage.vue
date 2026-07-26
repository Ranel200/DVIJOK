<template>
  <div class="settings-page">
    <AdminHeader :tabs="tabs" v-model:active-tab="activeTab" :gap="0" />

    <ServiceSettingsTab
      v-if="activeTab === 'service'"
      v-model:form="form"
      :subscription="subscription"
    />
    <SecuritySettingsTab
      v-else-if="activeTab === 'security'"
      :service-name="form.name"
      v-model:security="security"
      @logout="logoutConfirmOpen = true"
    />

    <BaseModal v-model="logoutConfirmOpen">
      <div class="logout-modal">
        <h2 class="logout-modal__title">
          Вы уверены, что хотите
          <br />
          выйти из аккаунта?
        </h2>
        <div class="logout-modal__actions">
          <BaseButton color="green" size="lg" @click="logoutConfirmOpen = false">Отмена</BaseButton>
          <BaseButton color="red" size="lg" :loading="logoutLoading" @click="confirmLogout">
            Да, выйти
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <BaseModal v-model="logoutDoneOpen" persistent @close="finishLogout">
      <div class="logout-modal">
        <h2 class="logout-modal__title">Вы вышли</h2>
        <BaseButton color="blue1" size="lg" @click="finishLogout">Ок</BaseButton>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import SecuritySettingsTab from '@/components/settings/SecuritySettingsTab.vue'
import ServiceSettingsTab from '@/components/settings/ServiceSettingsTab.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import { settingsApi } from '@/api/index.js'
import { useAuthStore } from '@/stores/auth.js'
import { detectClientSession } from '@/utils/sessionInfo.js'

const router = useRouter()
const authStore = useAuthStore()

const tabs = [
  { label: 'Автосервис', value: 'service' },
  { label: 'Безопасность', value: 'security' }
]
const activeTab = ref('service')
const logoutConfirmOpen = ref(false)
const logoutDoneOpen = ref(false)
const logoutLoading = ref(false)

const form = ref({
  name: '',
  headName: '',
  legalType: '',
  taxSystem: '',
  inn: '',
  ogrn: '',
  phone: '',
  description: ''
})

const subscription = ref({
  status: 'active',
  plan: 'PRO',
  activeUntil: '',
  daysLeft: 0,
  usedMonths: 0,
  totalMonths: 12,
  features: []
})

const security = ref({
  currentPassword: '',
  passwordChangedAt: '',
  emailConfirmEnabled: false,
  email: '',
  phoneConfirmEnabled: false,
  phone: '',
  sessions: [],
  loginHistory: []
})

async function confirmLogout() {
  logoutLoading.value = true
  try {
    await authStore.logout()
    logoutConfirmOpen.value = false
    logoutDoneOpen.value = true
  } finally {
    logoutLoading.value = false
  }
}

function finishLogout() {
  logoutDoneOpen.value = false
  router.push({ name: 'login' })
}

function applyCurrentSessionInfo() {
  const client = detectClientSession()
  security.value.sessions = (security.value.sessions || []).map(session => {
    if (!session.current) return session
    return { ...session, ...client }
  })
}

onMounted(async () => {
  const data = await settingsApi.get()
  if (data?.service) {
    form.value = { ...form.value, ...data.service }
  }
  if (data?.subscription) {
    subscription.value = { ...subscription.value, ...data.subscription }
  }
  if (data?.security) {
    security.value = { ...security.value, ...data.security }
  }
  applyCurrentSessionInfo()
})
</script>

<style scoped lang="scss">
.settings-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 0;
  overflow: hidden;
}

.logout-modal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.logout-modal__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 24px;
  font-weight: 600;
  line-height: 29px;
  text-align: center;
}

.logout-modal__actions {
  display: flex;
  align-items: center;
  gap: 90px;
}
</style>
