const routes = [
  {
    path: '/',
    component: () => import('@/layouts/SiteLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/pages/HomePage.vue'),
        meta: { title: 'Главная' }
      },
      {
        path: 'for-services',
        name: 'for-services',
        component: () => import('@/pages/ForServicesPage.vue'),
        meta: { title: 'Автосервисам' }
      },
      {
        path: 'for-owners',
        name: 'for-owners',
        component: () => import('@/pages/ForOwnersPage.vue'),
        meta: { title: 'Автовладельцам' }
      },
      {
        path: 'faq',
        name: 'faq',
        component: () => import('@/pages/FaqPage.vue'),
        meta: { title: 'FAQ' }
      }
    ]
  },

  {
    path: '/:catchAll(.*)*',
    name: 'not-found',
    component: () => import('@/pages/ErrorNotFound.vue'),
    meta: { title: 'Страница не найдена' }
  }
]

export default routes
