import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/index.js'
import { configureAuthFlow, setAuthToken } from '@dvijok/shared/api/http.js'

configureAuthFlow({
  refresh: '/client-auth/refresh',
  publicPaths: ['/client-auth/otp/request', '/client-auth/otp/verify', '/client-auth/refresh']
})

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  let initialized = false

  const isAuthenticated = computed(() => Boolean(token.value))

  function clearSession() {
    token.value = null
    user.value = null
    setAuthToken(null)
  }

  async function init() {
    if (initialized) return
    initialized = true
    try {
      const session = await authApi.restoreSession()
      token.value = session.token
      user.value = session.user
      setAuthToken(session.token)
    } catch {
      clearSession()
    }
  }

  async function login(credentials) {
    const session = await authApi.verifyOtp(credentials)
    token.value = session.token
    user.value = session.user
    setAuthToken(session.token)
    return session.user
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  async function updateProfile(payload = {}) {
    if (!user.value) return null
    const savedUser = await authApi.updateProfile({
      name: payload.name ?? user.value.name
    })
    user.value = {
      ...user.value,
      ...savedUser,
      email: payload.email ?? user.value.email
    }
    return user.value
  }

  return {
    user,
    token,
    isAuthenticated,
    clearSession,
    init,
    login,
    logout,
    updateProfile
  }
})
