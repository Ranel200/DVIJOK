import { boot } from 'quasar/wrappers'
import { useAuthStore } from '@/stores/auth.js'
import { setAuthFailureHandler } from '@dvijok/shared/api/http.js'

export default boot(async ({ store, router }) => {
  const auth = useAuthStore(store)
  setAuthFailureHandler(() => {
    auth.clearSession()
    if (router.currentRoute.value.name !== 'login') {
      router.replace({ name: 'login' })
    }
  })
  await auth.init()
})
