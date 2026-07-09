import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/index.js'
import { setAuthToken } from '@/api/http.js'

// Mock-авторизация. По умолчанию пользователь считается авторизованным (dev),
// чтобы навигация работала до появления реальной формы входа.
// Для строгой блокировки задайте начальные значения null/false.
export const useAuthStore = defineStore('auth', () => {
  const user = ref({
    id: 1,
    name: 'Администратор',
    email: 'admin@dvijok.local'
  })
  const token = ref('mock-token')

  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    const { token: nextToken, user: nextUser } =
      await authApi.login(credentials)
    token.value = nextToken
    user.value = nextUser
    setAuthToken(nextToken)
    return nextUser
  }

  async function logout() {
    await authApi.logout()
    token.value = null
    user.value = null
    setAuthToken(null)
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout
  }
})
