import { boot } from 'quasar/wrappers'
import { useAuthStore } from '@/stores/auth.js'

export default boot(async ({ store }) => {
  const auth = useAuthStore(store)
  await auth.init()
})
