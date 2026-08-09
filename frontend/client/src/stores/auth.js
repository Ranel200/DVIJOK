import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { setAuthToken } from '@dvijok/shared/api/http.js'

// Auth клиентского кабинета. Стартует без сессии — формы входа/регистрации
// доступны сразу. login/logout — заглушки до появления реального API.
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    token.value = 'mock-token'
    user.value = {
      id: 1,
      name: credentials?.name || 'Клиент',
      email: credentials?.email || 'client@dvijok.local',
      phone: credentials?.phone || ''
    }
    setAuthToken(token.value)
    return user.value
  }

  async function logout() {
    token.value = null
    user.value = null
    setAuthToken(null)
  }

  async function updateProfile(payload = {}) {
    if (!user.value) return null
    user.value = {
      ...user.value,
      name: payload.name ?? user.value.name,
      phone: payload.phone ?? user.value.phone,
      email: payload.email ?? user.value.email
    }
    return user.value
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    updateProfile
  }
})
