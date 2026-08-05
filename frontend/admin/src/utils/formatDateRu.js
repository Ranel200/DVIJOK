const MONTHS_GENITIVE = [
  'января',
  'февраля',
  'марта',
  'апреля',
  'мая',
  'июня',
  'июля',
  'августа',
  'сентября',
  'октября',
  'ноября',
  'декабря'
]

const MONTHS_SHORT = [
  'янв.',
  'фев.',
  'мар.',
  'апр.',
  'мая',
  'июн.',
  'июл.',
  'авг.',
  'сен.',
  'окт.',
  'ноя.',
  'дек.'
]

export function formatRuDate(iso) {
  if (!iso) return ''
  const d = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getDate()} ${MONTHS_GENITIVE[d.getMonth()]} ${d.getFullYear()}`
}

export function formatDeadlineUntil(date) {
  if (!date) return ''
  let iso = date
  if (date.includes('.')) {
    const [d, m, y] = date.split('.')
    iso = y ? `${y}-${m}-${d}` : ''
  }
  if (!iso) return ''
  const parsed = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(parsed.getTime())) return ''
  return `До ${parsed.getDate()} ${MONTHS_GENITIVE[parsed.getMonth()]}`
}

export function formatRuDateShort(iso) {
  if (!iso) return ''
  const d = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(d.getTime())) return ''
  return `${d.getDate()} ${MONTHS_SHORT[d.getMonth()]} ${d.getFullYear()}`
}

export function formatDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const date = `${d.getDate()} ${MONTHS_SHORT[d.getMonth()]} ${d.getFullYear()}`
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${date}, ${hours}:${minutes}`
}

export function startOfWeek(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + diff)
  return d
}

export function formatWeekRange(date) {
  const start = startOfWeek(date)
  const end = new Date(start)
  end.setDate(end.getDate() + 6)

  const sameMonth = start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()
  if (sameMonth) {
    return `${start.getDate()} — ${end.getDate()} ${MONTHS_GENITIVE[start.getMonth()]} ${start.getFullYear()}`
  }

  if (start.getFullYear() === end.getFullYear()) {
    return `${start.getDate()} ${MONTHS_GENITIVE[start.getMonth()]} — ${end.getDate()} ${MONTHS_GENITIVE[end.getMonth()]} ${start.getFullYear()}`
  }

  return `${start.getDate()} ${MONTHS_GENITIVE[start.getMonth()]} ${start.getFullYear()} — ${end.getDate()} ${MONTHS_GENITIVE[end.getMonth()]} ${end.getFullYear()}`
}

export function formatWeekdayDay(date) {
  const WEEKDAY_SHORT = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
  const d = date instanceof Date ? date : new Date(date)
  return `${WEEKDAY_SHORT[d.getDay()]}, ${d.getDate()} ${MONTHS_GENITIVE[d.getMonth()]}`
}
