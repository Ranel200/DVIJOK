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
    path: '/r/:referralCode',
    component: () => import('@/layouts/ClientAuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'referral',
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
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/SettingsPage.vue'),
        meta: { title: 'Настройки', requiresAuth: true }
      },
      {
        path: 'cars/new',
        name: 'car-create',
        component: () => import('@/pages/CarFormPage.vue'),
        meta: { title: 'Добавить автомобиль', requiresAuth: true }
      },
      {
        path: 'cars/:id/edit',
        name: 'car-edit',
        component: () => import('@/pages/CarFormPage.vue'),
        meta: { title: 'Изменить автомобиль', requiresAuth: true }
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
