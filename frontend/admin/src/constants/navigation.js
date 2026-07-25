export const adminNavigation = [
  { label: 'Расписание', icon: '/admin/icons/sidebar/schedule.svg', to: { name: 'schedule' } },
  { label: 'CRM', icon: '/admin/icons/sidebar/crm.svg', to: { name: 'crm' } },
  { label: 'Услуги', icon: '/admin/icons/sidebar/services.svg', to: { name: 'services' } },
  { label: 'Задачник', icon: '/admin/icons/sidebar/tasks.svg', to: { name: 'tasks' } },
  { label: 'QR-код', icon: '/admin/icons/sidebar/qr.svg', to: { name: 'qr' } },
  {
    label: 'Настройки',
    icon: '/admin/icons/sidebar/settings.svg',
    to: { name: 'settings' },
    pinBottom: true
  }
]
