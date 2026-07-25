const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/ClientAuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'client-login',
        component: () => import('@/pages/auth/LoginPage.vue'),
        meta: { title: 'Вход' }
      }
    ]
  },

  {
    path: '/',
    component: () => import('@/layouts/ClientLayout.vue'),
    children: [
      {
        path: '',
        name: 'client-dashboard',
        component: () => import('@/pages/DashboardPage.vue'),
        meta: { title: 'Кабинет', requiresAuth: true }
      }
    ]
  },

  // Always leave this as last one
  {
    path: '/:catchAll(.*)*',
    name: 'not-found',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
