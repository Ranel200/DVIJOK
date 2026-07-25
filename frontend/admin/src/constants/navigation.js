// Пункты бокового меню админки. Единый источник правды для сайдбара.
export const adminNavigation = [
  { label: 'Расписание', icon: 'event', to: { name: 'schedule' } },
  { label: 'CRM', icon: 'groups', to: { name: 'crm' } },
  { label: 'Услуги', icon: 'build', to: { name: 'services' } },
  { label: 'Задачник', icon: 'task_alt', to: { name: 'tasks' } },
  { label: 'QR-код', icon: 'qr_code', to: { name: 'qr' } },
  { label: 'Настройки', icon: 'settings', to: { name: 'settings' } }
]
