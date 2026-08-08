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
  { value: 'diagnostics', label: 'Диагностика', price: 2500 },
  { value: 'oil', label: 'Замена масла', price: 3200 },
  { value: 'tires', label: 'Шиномонтаж', price: 1800 },
  { value: 'brakes', label: 'Тормозная система', price: 4500 }
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

const mockBranches = [
  {
    id: 'branch-1',
    name: 'Папин гараж',
    address: 'ул. Улица, 14/1',
    isOpen: true,
    until: '21:00',
    mapSrc: '/client/icons/record/map.png'
  },
  {
    id: 'branch-2',
    name: 'Папин гараж',
    address: 'ул. Баумана, 45',
    isOpen: true,
    until: '20:00',
    mapSrc: '/client/icons/record/map.png'
  },
  {
    id: 'branch-3',
    name: 'Папин гараж',
    address: 'пр. Победы, 120',
    isOpen: false,
    until: '10:00',
    mapSrc: '/client/icons/record/map.png'
  }
]

const mockSpecialists = [
  {
    id: 's1',
    name: 'Иванов Алексей',
    role: 'Старший мастер',
    avatarColor: 'var(--dvijok-accent-coral)',
    rating: 4.2,
    reviews: 18,
    price: 5500,
    nearestDate: 'четверг, 6 августа',
    slots: ['10:00', '11:00', '12:00', '14:00', '15:30', '17:00']
  },
  {
    id: 's2',
    name: 'Петров Сергей',
    role: 'Мастер',
    avatarColor: 'var(--dvijok-accent-cyan)',
    rating: 4.8,
    reviews: 56,
    price: 4500,
    nearestDate: 'пятница, 7 августа',
    slots: ['10:00', '13:00', '16:00', '18:00']
  },
  {
    id: 's3',
    name: 'Сидоров Дмитрий',
    role: 'Механик',
    avatarColor: 'var(--dvijok-blue-pale)',
    rating: 4.5,
    reviews: 34,
    price: 3800,
    nearestDate: 'суббота, 8 августа',
    slots: ['11:00', '12:30', '15:00']
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

export const branchesApi = {
  async list(params = {}) {
    if (USE_MOCK) {
      return mockOk({
        city: 'Казань',
        branches: mockBranches
      })
    }
    return http.get('/branches', { params })
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
  },

  async specialists(params = {}) {
    if (USE_MOCK) {
      return mockOk({
        specialists: mockSpecialists
      })
    }
    return http.get('/booking/specialists', { params })
  }
}

const mockCars = [
  {
    id: 'car-1',
    brand: 'Toyota Camry',
    year: 2019,
    color: 'Белый',
    plate: 'А 123 ВС 116',
    vin: '12345678912345678',
    nextAppointment: {
      serviceName: 'ПАПИН ГАРАЖ',
      datetime: '31 июля 13:00',
      service: 'Диагностика',
      master: 'Кузнецов Сергей',
      car: 'Toyota Camry'
    },
    maintenance: [
      { label: 'Крайний пробег', value: '66 000 км' },
      { label: 'Масло', value: 'замена на 80 000' },
      { label: 'ТО', value: 'рекомендовано на 100 000' }
    ],
    repair: {
      orderNumber: '001',
      carLabel: 'Toyota Camry',
      statuses: [
        {
          id: 'booked',
          title: 'Записан',
          subtitle: '14 июля 2026 · 15:00',
          color: '#093095',
          state: 'done'
        },
        {
          id: 'in_progress',
          title: 'В работе',
          subtitle: 'Работает мастер Кузнецов Д.',
          color: '#D45813',
          state: 'done'
        },
        {
          id: 'needs_approval',
          title: '! Нуждается в согласовании',
          subtitle: 'Ожидает вашего ответа',
          color: '#430890',
          state: 'current',
          action: 'Связаться с мастером'
        },
        {
          id: 'not_ready',
          title: 'Еще не готово',
          subtitle: 'Ожидайте выполнения услуги',
          color: '#157848',
          state: 'inactive'
        }
      ]
    }
  },
  {
    id: 'car-2',
    brand: 'Kia Rio',
    year: 2021,
    color: 'Серый',
    plate: 'В 456 ОР 116',
    vin: '98765432109876543',
    nextAppointment: {
      serviceName: 'МоторПро',
      datetime: '5 августа 11:00',
      service: 'Замена масла',
      master: 'Иванов Алексей',
      car: 'Kia Rio'
    },
    maintenance: [
      { label: 'Крайний пробег', value: '42 500 км' },
      { label: 'Масло', value: 'замена на 50 000' },
      { label: 'ТО', value: 'рекомендовано на 60 000' }
    ],
    repair: {
      orderNumber: '014',
      carLabel: 'Kia Rio',
      statuses: [
        {
          id: 'booked',
          title: 'Записан',
          subtitle: '2 июня 2026 · 11:00',
          color: '#093095',
          state: 'done'
        },
        {
          id: 'in_progress',
          title: 'В работе',
          subtitle: 'Работает мастер Иванов А.',
          color: '#D45813',
          state: 'done'
        },
        {
          id: 'needs_approval',
          title: '! Нуждается в согласовании',
          subtitle: 'Ожидает вашего ответа',
          color: '#430890',
          state: 'current',
          action: 'Связаться с мастером'
        },
        {
          id: 'not_ready',
          title: 'Еще не готово',
          subtitle: 'Ожидайте выполнения услуги',
          color: '#157848',
          state: 'inactive'
        }
      ]
    }
  }
]

const mockBots = [
  { id: 'tg', label: '@BOT_tg', icon: '/client/icons/my-car/tg.png', href: '#' },
  { id: 'vk', label: '@BOT_vk', icon: '/client/icons/my-car/vk.png', href: '#' },
  { id: 'max', label: '@BOT_max', icon: '/client/icons/my-car/max.png', href: '#' }
]

export const carsApi = {
  async list() {
    if (USE_MOCK) {
      return mockOk({
        cars: mockCars,
        bots: mockBots
      })
    }
    return http.get('/cars')
  }
}

const mockHistoryItems = [
  {
    id: 'hist-1',
    title: 'Замена масла и фильтров',
    status: 'new',
    carBrand: 'Марка машины',
    carPlate: 'Х 000 ХХ 116',
    serviceName: 'Папин гараж',
    serviceAddress: 'ул. Автозаводская, 14/1',
    master: 'Кузнецов Д.',
    datetime: '31.07.2026 13:00',
    amount: 5500,
    orderNumber: '008',
    orderReady: false,
    monthLabel: 'Июль 2026'
  },
  {
    id: 'hist-2',
    title: 'Диагностика подвески',
    status: 'in_progress',
    carBrand: 'Марка машины',
    carPlate: 'Х 000 ХХ 116',
    serviceName: 'Папин гараж',
    serviceAddress: 'ул. Автозаводская, 14/1',
    master: 'Кузнецов Д.',
    datetime: '28.07.2026 11:00',
    amount: 3200,
    orderNumber: '009',
    orderReady: false,
    monthLabel: 'Июль 2026'
  },
  {
    id: 'hist-3',
    title: 'Ремонт тормозной системы',
    status: 'approval',
    carBrand: 'Марка машины',
    carPlate: 'Х 000 ХХ 116',
    serviceName: 'Папин гараж',
    serviceAddress: 'ул. Автозаводская, 14/1',
    master: 'Иванов А.',
    datetime: '25.07.2026 15:00',
    amount: 9800,
    orderNumber: '010',
    orderReady: false,
    monthLabel: 'Июль 2026'
  },
  {
    id: 'hist-4',
    title: 'Техническое обслуживание',
    status: 'completed',
    carBrand: 'Марка машины',
    carPlate: 'Х 000 ХХ 116',
    serviceName: 'Папин гараж',
    serviceAddress: 'ул. Автозаводская, 14/1',
    master: 'Кузнецов Д.',
    datetime: '09.07.2026 13:00',
    amount: 7000,
    orderNumber: '007',
    orderReady: true,
    monthLabel: 'Июль 2026'
  },
  {
    id: 'hist-5',
    title: 'Замена сцепления',
    status: 'completed',
    carBrand: 'Марка машины',
    carPlate: 'Х 000 ХХ 116',
    serviceName: 'У дяди Васи',
    serviceAddress: 'ул. Ленина, 67',
    master: 'Лобанов С.',
    datetime: '12.05.2026 11:00',
    amount: 15000,
    orderNumber: '006',
    orderReady: true,
    monthLabel: 'Май 2026'
  }
]

export const historyApi = {
  async list(params = {}) {
    if (USE_MOCK) {
      return mockOk({ items: mockHistoryItems })
    }
    return http.get('/history', { params })
  }
}
