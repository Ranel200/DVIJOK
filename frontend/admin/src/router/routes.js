const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/pages/auth/LoginPage.vue'),
        meta: { title: 'Вход' }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/pages/auth/RegisterPage.vue'),
        meta: { title: 'Регистрация' }
      }
    ]
  },

  {
    path: '/tariffs',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: '',
        name: 'tariffs',
        component: () => import('@/pages/auth/TariffsPage.vue'),
        meta: { title: 'Тарифы', requiresAuth: true }
      }
    ]
  },

  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    children: [
      {
        path: '',
        name: 'schedule',
        component: () => import('@/pages/SchedulePage.vue'),
        meta: { title: 'Расписание', requiresAuth: true }
      },
      {
        path: 'crm',
        name: 'crm',
        component: () => import('@/pages/CrmPage.vue'),
        meta: { title: 'Заказы', requiresAuth: true }
      },
      {
        path: 'services',
        name: 'services',
        component: () => import('@/pages/ServicesPage.vue'),
        meta: { title: 'Услуги', requiresAuth: true }
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('@/pages/TasksPage.vue'),
        meta: { title: 'Задачи', requiresAuth: true }
      },
      {
        path: 'qr',
        name: 'qr',
        component: () => import('@/pages/QrPage.vue'),
        meta: { title: 'QR-код', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/pages/SettingsPage.vue'),
        meta: { title: 'Настройки', requiresAuth: true }
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
