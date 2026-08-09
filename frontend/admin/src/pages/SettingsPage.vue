<template>
  <div class="settings-page">
    <AdminHeader :tabs="tabs" v-model:active-tab="activeTab" :gap="0" />

    <ServiceSettingsTab
      v-show="activeTab === 'service'"
      ref="serviceTabRef"
      v-model:form="form"
      :subscription="subscription"
      @saved="onServiceSaved"
    />
    <SecuritySettingsTab
      v-show="activeTab === 'security'"
      :service-name="form.name"
      :email="form.email"
      :phone="form.phone"
      v-model:security="security"
      @logout="logoutConfirmOpen = true"
      @edit-service="openServiceEdit"
    />
    <DocumentsSettingsTab
      v-show="activeTab === 'documents'"
      :accepted-at-by-id="documents.acceptedAtById"
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

    <SuccessModal
      v-model="logoutDoneOpen"
      message="Вы вышли"
      persistent
      @confirm="finishLogout"
      @close="finishLogout"
    />
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import DocumentsSettingsTab from '@/components/settings/DocumentsSettingsTab.vue'
import SecuritySettingsTab from '@/components/settings/SecuritySettingsTab.vue'
import ServiceSettingsTab from '@/components/settings/ServiceSettingsTab.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'
import { settingsApi } from '@/api/index.js'
import { useAuthStore } from '@/stores/auth.js'
import { detectClientSession } from '@/utils/sessionInfo.js'

const router = useRouter()
const authStore = useAuthStore()

const tabs = [
  { label: 'Автосервис', value: 'service' },
  { label: 'Безопасность', value: 'security' },
  { label: 'Документы', value: 'documents' }
]
const activeTab = ref('service')
const serviceTabRef = ref(null)
const logoutConfirmOpen = ref(false)
const logoutDoneOpen = ref(false)
const logoutLoading = ref(false)

async function openServiceEdit(fieldKey) {
  await nextTick()
  serviceTabRef.value?.openEdit(fieldKey)
}

function onServiceSaved(payload) {
  if (payload?.email != null) security.value.email = payload.email
  if (payload?.phone != null) security.value.phone = payload.phone
}

const form = ref({
  name: '',
  headName: '',
  legalType: '',
  taxSystem: '',
  inn: '',
  ogrn: '',
  bankAccount: '',
  phone: '',
  email: '',
  address: '',
  logo: '',
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
  securityLevel: 'medium',
  emailConfirmEnabled: false,
  email: '',
  phoneConfirmEnabled: false,
  phone: '',
  sessions: [],
  loginHistory: []
})

const documents = ref({
  acceptedAtById: {}
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
  if (data?.documents) {
    documents.value = { ...documents.value, ...data.documents }
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
