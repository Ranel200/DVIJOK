import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/index.js'
import { setAuthToken } from '@dvijok/shared/api/http.js'

// Auth-стор админки. Строгий режим: по умолчанию не авторизован,
// форма входа доступна для проверки моков.
// Демо-доступ: admin / admin
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function clearSession() {
    token.value = null
    user.value = null
    setAuthToken(null)
  }

  async function init() {
    try {
      const { token: nextToken, user: nextUser } = await authApi.restoreSession()
      user.value = nextUser
      if (nextToken !== undefined) {
        token.value = nextToken
        setAuthToken(nextToken)
      }
    } catch {
      clearSession()
    }
  }

  async function login(credentials) {
    const { token: nextToken, user: nextUser } = await authApi.login(credentials)
    token.value = nextToken
    user.value = nextUser
    setAuthToken(nextToken)
    return nextUser
  }

  async function register(payload) {
    const { token: nextToken, user: nextUser } = await authApi.register(payload)
    token.value = nextToken
    user.value = nextUser
    setAuthToken(nextToken)
    return nextUser
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    clearSession,
    init,
    login,
    register,
    logout
  }
})
