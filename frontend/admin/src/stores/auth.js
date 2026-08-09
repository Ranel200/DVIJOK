import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/index.js'
import { setAuthToken } from '@dvijok/shared/api/http.js'
import { STAFF_ACCESS_KEYS, firstAccessiblePage } from '@/constants/staff.js'

// Auth-стор админки. Строгий режим: по умолчанию не авторизован.
// Демо-владелец: admin / admin
// Демо-сотрудники: smirnov, sidorov, petrov, morozova, sokolova (пароль = логин)
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)

  const isAuthenticated = computed(() => Boolean(token.value))
  const isOwner = computed(() => Boolean(user.value?.isOwner))
  const subscriptionPlan = computed(() => user.value?.subscriptionPlan ?? 'none')
  const hasSubscription = computed(() => Boolean(user.value) && subscriptionPlan.value !== 'none')

  const homeRoute = computed(() => {
    if (!isAuthenticated.value) return { name: 'login' }
    if (!hasSubscription.value) return { name: 'tariffs' }
    const page = firstAccessiblePage(user.value?.access, { isOwner: isOwner.value })
    return page ? { name: page } : { name: 'not-found' }
  })

  function canAccess(permission) {
    if (!permission) return true
    if (!isAuthenticated.value) return false
    if (isOwner.value) return true
    if (!STAFF_ACCESS_KEYS.includes(permission)) return false
    return Boolean(user.value?.access?.[permission])
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
      token.value = null
      user.value = null
      setAuthToken(null)
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
    await authApi.logout()
    token.value = null
    user.value = null
    setAuthToken(null)
  }

  async function selectSubscriptionPlan(plan) {
    const { user: nextUser } = await authApi.selectSubscriptionPlan(plan)
    user.value = nextUser
    return nextUser
  }

  return {
    user,
    token,
    isAuthenticated,
    isOwner,
    subscriptionPlan,
    hasSubscription,
    homeRoute,
    canAccess,
    init,
    login,
    register,
    selectSubscriptionPlan,
    logout
  }
})
