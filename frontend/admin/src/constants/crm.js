export const CRM_STATUS = {
  new: {
    label: 'Новая сделка',
    color: 'var(--dvijok-blue-primary)',
    bg: 'var(--dvijok-choice-active)'
  },
  in_progress: { label: 'В работе', color: '#D45813', bg: '#FFCCAE' },
  approval: { label: 'Согласование', color: '#430890', bg: '#D7BCFB' },
  done: { label: 'Готово', color: '#2F8527', bg: '#CEFFA2' }
}

export const CRM_STATUS_LIST = Object.entries(CRM_STATUS).map(([value, { label, color, bg }]) => ({
  value,
  label,
  color,
  bg
}))

export const ORDER_SOURCE_OPTIONS = [
  { value: 'call', label: 'Звонок' },
  { value: 'website', label: 'Сайт' },
  { value: 'avito', label: 'Avito' },
  { value: 'referral', label: 'Рекомендация' },
  { value: 'walk_in', label: 'Визит' },
  { value: 'other', label: 'Другое' }
]

export function crmStatusOption(value) {
  return (
    CRM_STATUS[value] || {
      label: value,
      color: 'var(--dvijok-link-hover)',
      bg: 'var(--dvijok-muted)'
    }
  )
}

export function formatCrmMoney(value) {
  return Number(value || 0).toLocaleString('ru-RU')
}

export function formatCrmOrderNumber(number) {
  return `№${String(number).padStart(3, '0')}`
}

export function matchesCrmSearch(item, search) {
  const query = (search || '').trim().toLowerCase()
  if (!query) return true
  const numberStr = String(item.number)
  const formatted = formatCrmOrderNumber(item.number).toLowerCase()
  const name = (item.clientName || '').toLowerCase()
  return numberStr.includes(query) || formatted.includes(query) || name.includes(query)
}

export function filterCrmDeals(deals, { search = '', statusFilter = [] } = {}) {
  return (deals || []).filter(deal => {
    const statusOk = !statusFilter.length || statusFilter.includes(deal.status)
    return statusOk && matchesCrmSearch(deal, search)
  })
}
