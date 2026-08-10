import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import routes from './routes.js'
import { useAuthStore } from '@/stores/auth.js'
import { STAFF_ACCESS_KEYS } from '@/constants/staff.js'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */
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

  // Mock-гард: авторизация, подписка, доступы сотрудника к страницам.
  Router.beforeEach(to => {
    const auth = useAuthStore()

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: 'login' }
    }

    if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
      return auth.homeRoute
    }

    if (to.name === 'tariffs') {
      if (!auth.isAuthenticated) return { name: 'login' }
      if (!auth.isOwner) return auth.homeRoute
      return true
    }

    if (auth.isAuthenticated && !auth.hasSubscription) {
      return { name: 'tariffs' }
    }

    const permission = STAFF_ACCESS_KEYS.includes(to.name) ? to.name : null
    if (permission && !auth.canAccess(permission)) {
      return auth.homeRoute
    }

    return true
  })

  return Router
})
