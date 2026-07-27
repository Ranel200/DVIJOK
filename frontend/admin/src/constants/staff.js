export const STAFF_COLORS = [
  { value: '#FF6F53', label: 'Персик' },
  { value: '#A70007', label: 'Помидор' },
  { value: '#F03272', label: 'Фламинго' },
  { value: '#F3B0E3', label: 'Сирень' },
  { value: '#FFAD01', label: 'Желток' },
  { value: '#FFFC3B', label: 'Лимон' },
  { value: '#0E4943', label: 'Лес' },
  { value: '#9AB3EB', label: 'Дымка' },
  { value: '#E2D29C', label: 'Крем' },
  { value: '#A0E0C8', label: 'Мята' },
  { value: '#7679EC', label: 'Черника' },
  { value: '#0ABCCA', label: 'Бирюза' }
]

export const STAFF_ROLE_OPTIONS = [
  { value: 'senior_admin', label: 'Старший администратор' },
  { value: 'junior_admin', label: 'Младший администратор' },
  { value: 'senior_master', label: 'Старший мастер' },
  { value: 'junior_master', label: 'Младший мастер' }
]

export const STAFF_ROLE_LABELS = Object.fromEntries(
  STAFF_ROLE_OPTIONS.map(item => [item.value, item.label])
)

export const STAFF_ACCESS_OPTIONS = [
  { key: 'schedule', label: 'Расписание' },
  { key: 'crm', label: 'CRM' },
  { key: 'services', label: 'Услуги' },
  { key: 'tasks', label: 'Задачник' },
  { key: 'qr', label: 'QR-код' },
  { key: 'settings', label: 'Настройки' }
]

export function mapLegacyRole(role) {
  const value = String(role || '')
  if (STAFF_ROLE_LABELS[value]) return value
  if (value === 'Администратор' || value === 'Владелец') return 'senior_admin'
  if (value === 'Менеджер') return 'junior_admin'
  if (value === 'Мастер') return 'senior_master'
  return 'senior_master'
}

export function formatStaffRate(value) {
  const digits = String(value ?? '').replace(/\D/g, '')
  if (!digits) return ''
  return `${Number(digits).toLocaleString('ru-RU')} ₽`
}

export function parseStaffRate(value) {
  return String(value ?? '').replace(/\D/g, '')
}
