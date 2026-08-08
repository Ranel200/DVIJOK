const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/ClientAuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/pages/auth/AuthPage.vue'),
        meta: { title: 'Вход' }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/pages/auth/AuthPage.vue'),
        meta: { title: 'Регистрация' }
      }
    ]
  },

  {
    path: '/',
    component: () => import('@/layouts/ClientLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/pages/HomePage.vue'),
        meta: { title: 'Кабинет', requiresAuth: true }
      },
      {
        path: 'booking',
        name: 'booking',
        component: () => import('@/pages/BookingPage.vue'),
        meta: { title: 'Запись' }
      }
    ]
  },

  {
    path: '/:catchAll(.*)*',
    name: 'not-found',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
