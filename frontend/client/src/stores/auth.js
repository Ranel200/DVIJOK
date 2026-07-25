import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { setAuthToken } from '@dvijok/shared/api/http.js'

// Mock-авторизация клиентского кабинета. По умолчанию пользователь считается
// авторизованным (dev), чтобы навигация работала до появления реальной формы
// входа и API. Для строгой блокировки задайте начальные значения null/false.
// login/logout — заглушки; подключение authApi — когда появится бэкенд.
export const useAuthStore = defineStore('auth', () => {
  const user = ref({
    id: 1,
    name: 'Клиент',
    email: 'client@dvijok.local'
  })
  const token = ref('mock-token')

  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    token.value = 'mock-token'
    user.value = {
      id: 1,
      name: 'Клиент',
      email: credentials?.email || 'client@dvijok.local'
    }
    setAuthToken(token.value)
    return user.value
  }

  async function logout() {
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
