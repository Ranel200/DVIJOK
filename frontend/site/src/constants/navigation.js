export const siteNavigation = [
  { label: 'Автосервисам', to: { name: 'for-services' } },
  { label: 'Автовладельцам', to: { name: 'for-owners' } },
  { label: 'Тарифы' },
  { label: 'Блог', to: { name: 'blog' } },
  { label: 'FAQ' }
]

export const footerColumns = [
  {
    id: 'product',
    title: 'Продукт',
    links: [
      { label: 'Автосервисам', to: { name: 'for-services' } },
      { label: 'Автовладельцам', to: { name: 'for-owners' } },
      { label: 'Автосервисы' },
      { label: 'Тарифы' }
    ]
  },
  {
    id: 'resources',
    title: 'Ресурсы',
    links: [
      { label: 'Автосервисам', to: { name: 'for-services' } },
      { label: 'Автовладельцам', to: { name: 'for-owners' } },
      { label: 'Автосервисы' },
      { label: 'Тарифы' }
    ]
  },
  {
    id: 'company',
    title: 'Компания',
    links: [{ label: 'О ДВИЖОК' }, { label: 'Контакты' }]
  },
  {
    id: 'documents',
    title: 'Документы',
    links: [
      {
        label: 'Пользовательское соглашение',
        lines: ['Пользовательское', 'соглашение'],
        href: '/docs/user-agreement.html'
      },
      {
        label: 'Политика конфиденциальности',
        lines: ['Политика', 'конфиденциальности'],
        href: '/docs/privacy-policy.html'
      },
      {
        label: 'Политика Cookies',
        href: '/docs/cookies-policy.html'
      }
    ]
  }
]
