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
        path: 'blog',
        name: 'blog',
        component: () => import('@/pages/BlogPage.vue'),
        meta: { title: 'Блог' }
      },
      {
        path: 'blog/:id',
        name: 'blog-article',
        component: () => import('@/pages/BlogArticlePage.vue'),
        meta: { title: 'Статья' }
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
