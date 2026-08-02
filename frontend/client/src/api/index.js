import { http, USE_MOCK } from '@dvijok/shared/api/http.js'
import { mockOk } from '@dvijok/shared/api/mock.js'

const DEFAULT_DESCRIPTION =
  'Автосервис полного цикла: диагностика, ремонт и обслуживание автомобилей. Качественная работа, опытные мастера и забота о вашем автомобиле.'

const mockYourServices = [
  {
    id: 'yours-1',
    name: 'Название',
    address: 'ул. Улица, 14/1',
    hours: 'Открыто до 21:00',
    description: DEFAULT_DESCRIPTION,
    rating: 4.2,
    reviews: 18,
    lastVisit: '14 июля 2026'
  },
  {
    id: 'yours-2',
    name: 'МоторПро',
    address: 'ул. Баумана, 45',
    hours: 'Открыто до 20:00',
    description: DEFAULT_DESCRIPTION,
    rating: 4.8,
    reviews: 56,
    lastVisit: '2 июня 2026'
  }
]

const mockAllServices = [
  {
    id: 'all-1',
    name: 'ДрайвСервис',
    address: 'пр. Победы, 120',
    hours: 'Открыто до 22:00',
    description: DEFAULT_DESCRIPTION,
    rating: 4.5,
    reviews: 34
  },
  {
    id: 'all-2',
    name: 'АвтоЛайн',
    address: 'ул. Чистопольская, 8',
    hours: 'Открыто до 19:00',
    description: DEFAULT_DESCRIPTION,
    rating: 4.1,
    reviews: 12
  },
  {
    id: 'all-3',
    name: 'ТехноДрайв',
    address: 'ул. Рихарда Зорге, 33',
    hours: 'Открыто до 21:00',
    description: DEFAULT_DESCRIPTION,
    rating: 4.7,
    reviews: 89
  }
]

const mockServiceOptions = [
  { value: 'diagnostics', label: 'Диагностика' },
  { value: 'oil', label: 'Замена масла' },
  { value: 'tires', label: 'Шиномонтаж' },
  { value: 'brakes', label: 'Тормозная система' }
]

const mockCarOptions = [
  { value: 'car-1', label: 'Toyota Camry · А123ВС 116' },
  { value: 'car-2', label: 'Kia Rio · В456ОР 116' },
  { value: 'car-3', label: 'Hyundai Solaris · С789КХ 116' }
]

const mockMasters = [
  {
    id: 'any',
    name: 'Любой мастер',
    subtitle: 'Определяется автоматически'
  },
  {
    id: 'm1',
    name: 'Иванов Алексей',
    subtitle: 'Услуги'
  },
  {
    id: 'm2',
    name: 'Петров Сергей',
    subtitle: 'Услуги'
  },
  {
    id: 'm3',
    name: 'Сидоров Дмитрий',
    subtitle: 'Услуги'
  }
]

const mockTimeSlots = [
  '10:00',
  '11:00',
  '12:00',
  '13:00',
  '14:00',
  '15:00',
  '16:00',
  '17:00',
  '18:00',
  '19:00',
  '20:00'
]

function matchesService(item, query) {
  const needle = query.trim().toLowerCase()
  if (!needle) return true
  return [item.name, item.address, item.description, item.hours]
    .filter(Boolean)
    .some(value => value.toLowerCase().includes(needle))
}

function isMockDayAvailable(day) {
  return day % 3 !== 0
}

export const servicesApi = {
  async list(params = {}) {
    if (USE_MOCK) {
      const query = params.query || ''
      return mockOk({
        city: 'г. Казань',
        yours: mockYourServices.filter(item => matchesService(item, query)),
        all: mockAllServices.filter(item => matchesService(item, query))
      })
    }
    return http.get('/services', { params })
  }
}

export const bookingApi = {
  async options(params = {}) {
    if (USE_MOCK) {
      return mockOk({
        serviceOptions: mockServiceOptions,
        carOptions: mockCarOptions,
        masters: mockMasters,
        timeSlots: mockTimeSlots
      })
    }
    return http.get('/booking/options', { params })
  },

  async availability(params = {}) {
    if (USE_MOCK) {
      const year = params.year
      const month = params.month
      const daysInMonth = new Date(year, month + 1, 0).getDate()
      const days = {}
      for (let day = 1; day <= daysInMonth; day += 1) {
        days[day] = isMockDayAvailable(day)
      }
      return mockOk({ days }, 0)
    }
    return http.get('/booking/availability', { params })
  },

  async create(payload) {
    if (USE_MOCK) {
      return mockOk({
        id: `booking-${Date.now()}`,
        ...payload
      })
    }
    return http.post('/booking', payload)
  }
}
