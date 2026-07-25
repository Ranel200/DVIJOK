import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import routes from './routes.js'
import { useAuthStore } from '@/stores/auth.js'

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
  })

  // Mock-гард авторизации. Пока auth-стор по умолчанию авторизован,
  // редиректов не происходит; логика готова к реальной блокировке.
  Router.beforeEach(to => {
    const auth = useAuthStore()

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'client-login' }
    }

    if (to.name === 'client-login' && auth.isAuthenticated) {
      return { name: 'client-dashboard' }
    }

    return true
  })

  return Router
})
