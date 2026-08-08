import { pluralize } from '@/utils/pluralize.js'

export const BOOKING_STEPS = new Set([
  'branches',
  'menu',
  'specialist',
  'service',
  'datetime',
  'details'
])

export const MENU_ITEMS = [
  {
    id: 'specialist',
    label: 'Выбрать специалиста',
    icon: '/client/icons/record/man.svg'
  },
  {
    id: 'service',
    label: 'Выбрать услугу',
    icon: '/client/icons/record/doc.svg'
  },
  {
    id: 'datetime',
    label: 'Выбрать дату и время',
    icon: '/client/icons/record/calendar.svg'
  }
]

export const WEEKDAYS = [
  { label: 'ПН', weekend: false },
  { label: 'ВТ', weekend: false },
  { label: 'СР', weekend: false },
  { label: 'ЧТ', weekend: false },
  { label: 'ПТ', weekend: false },
  { label: 'СБ', weekend: true },
  { label: 'ВС', weekend: true }
]

export const MONTH_NAMES = [
  'Январь',
  'Февраль',
  'Март',
  'Апрель',
  'Май',
  'Июнь',
  'Июль',
  'Август',
  'Сентябрь',
  'Октябрь',
  'Ноябрь',
  'Декабрь'
]

export const MONTH_NAMES_GEN = [
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

export const WEEKDAY_NAMES = [
  'воскресенье',
  'понедельник',
  'вторник',
  'среда',
  'четверг',
  'пятница',
  'суббота'
]

export const PLATE_MAIN_KINDS = ['letter', 'digit', 'digit', 'digit', 'letter', 'letter']
export const PLATE_LETTERS = 'АВЕКМНОРСТУХABEKMHOPCTYX'

export const PLATE_TYPE_OPTIONS = [
  { value: 'ru', label: 'Российский номер' },
  { value: 'foreign', label: 'Иностранный номер' }
]

export function toIso(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function formatPrice(value) {
  return `${Number(value).toLocaleString('ru-RU')} ₽`
}

export function hoursLabel(branch) {
  const prefix = branch.isOpen ? 'Открыто до' : 'Закрыто до'
  return `${prefix} ${branch.until}`
}

export function reviewsLabel(count) {
  return `${count} ${pluralize(count, ['отзыв', 'отзыва', 'отзывов'])}`
}

export function branchesTitle(count) {
  return `${count} ${pluralize(count, ['филиал', 'филиала', 'филиалов'])}`
}

export function formatDateLabel(iso) {
  if (!iso) return '—'
  const [year, month, day] = iso.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  const weekday = WEEKDAY_NAMES[date.getDay()]
  return `${weekday[0].toUpperCase()}${weekday.slice(1)}, ${day} ${MONTH_NAMES_GEN[month - 1]}`
}

export function formatTimeRange(time) {
  if (!time) return '—'
  const [hours, minutes] = time.split(':').map(Number)
  const endHours = String(hours + 1).padStart(2, '0')
  const endMinutes = String(minutes).padStart(2, '0')
  return `${time}-${endHours}:${endMinutes}`
}

export function radioColor(filled) {
  return filled ? 'var(--dvijok-success)' : 'var(--dvijok-text-secondary)'
}

export function buildCalendarCells(monthCursor, availableDays, today) {
  const year = monthCursor.getFullYear()
  const month = monthCursor.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7
  const monthGen = MONTH_NAMES_GEN[month]
  const cells = []
  const todayIso = toIso(today)

  for (let i = 0; i < firstWeekday; i += 1) {
    cells.push({ day: null, available: false, iso: '', caption: '' })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day)
    const iso = toIso(date)
    const isToday = iso === todayIso
    const isPast = date < today
    const available = !isPast && Boolean(availableDays[day])
    cells.push({
      day,
      iso,
      available: available || isToday,
      caption: isToday ? 'Сегодня' : monthGen.slice(0, 3),
      isToday
    })
  }

  while (cells.length % 7 !== 0) {
    cells.push({ day: null, available: false, iso: '', caption: '' })
  }

  return cells
}

export function dayClass(cell, selectedDate, prefix = 'datetime-step') {
  if (!cell.day) return `${prefix}__day--spacer`
  if (!cell.available) return `${prefix}__day--unavailable`
  return {
    [`${prefix}__day--today`]: cell.isToday,
    [`${prefix}__day--available`]: !cell.isToday,
    [`${prefix}__day--selected`]: cell.iso === selectedDate
  }
}
