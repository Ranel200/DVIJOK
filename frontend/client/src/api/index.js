import { http, refreshAuthToken, setAuthToken, USE_MOCK } from '@dvijok/shared/api/http.js'
import { mockOk } from '@dvijok/shared/api/mock.js'

function clientUser(profile) {
  return {
    id: profile.id,
    name: profile.full_name || 'Клиент',
    email: profile.email || '',
    phone: profile.phone
  }
}

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
  { value: 'repair', label: 'Ремонт', price: 5000 }
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

export const authApi = {
  async requestCode({ phone }) {
    if (USE_MOCK) {
      return mockOk({ detail: 'Код отправлен', debug_code: '1111' })
    }
    return http.post('/client-auth/otp/request', { phone })
  },

  async verifyOtp(payload) {
    if (USE_MOCK) {
      return mockOk({
        token: 'mock-token',
        user: {
          id: 1,
          name: payload.name || payload.full_name || 'Клиент',
          email: '',
          phone: payload.phone
        }
      })
    }
    const session = await http.post('/client-auth/otp/verify', {
      phone: payload.phone,
      code: payload.code,
      full_name: payload.name || payload.full_name || undefined,
      referral_code: payload.referral_code || undefined
    })
    const token = session.access_token
    setAuthToken(token)
    const profile = await http.get('/client-auth/me')
    return { token, user: clientUser(profile) }
  },

  async restoreSession() {
    if (USE_MOCK) throw new Error('Mock client session is not persistent')
    const token = await refreshAuthToken()
    const profile = await http.get('/client-auth/me')
    return { token, user: clientUser(profile) }
  },

  async logout() {
    if (USE_MOCK) return mockOk({ success: true })
    return http.post('/client-auth/logout')
  }
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
    return http.get('/client-portal/ui/services', { params })
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
  async publicContext(code) {
    return http.get(`/public-booking/${encodeURIComponent(code)}`)
  },

  async publicOptions(code) {
    return http.get(`/public-booking/${encodeURIComponent(code)}/options`)
  },

  async publicAvailability(code, params = {}) {
    return http.get(`/public-booking/${encodeURIComponent(code)}/availability`, { params })
  },

  async publicCreate(code, payload) {
    return http.post(`/public-booking/${encodeURIComponent(code)}`, payload)
  },

  async publicSpecialists(code) {
    return http.get(`/public-booking/${encodeURIComponent(code)}/specialists`)
  },

  async options(params = {}) {
    if (USE_MOCK) {
      return mockOk({
        serviceOptions: mockServiceOptions,
        carOptions: mockCarOptions,
        masters: mockMasters,
        timeSlots: mockTimeSlots
      })
    }
    return http.get('/client-portal/ui/booking/options', { params })
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
    return http.get('/client-portal/ui/booking/availability', { params })
  },

  async create(payload) {
    if (USE_MOCK) {
      return mockOk({
        id: `booking-${Date.now()}`,
        ...payload
      })
    }
    return http.post('/client-portal/ui/booking', payload)
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

function formatRuPlate(raw) {
  const cleaned = String(raw ?? '')
    .replace(/\s/g, '')
    .toUpperCase()
  if (cleaned.length < 6) return cleaned
  const main = cleaned.slice(0, 6)
  const region = cleaned.slice(6)
  return `${main[0]} ${main.slice(1, 4)} ${main.slice(4)}${region ? ` ${region}` : ''}`
}

function formatPlateDisplay(plate, plateType = 'ru') {
  if (!plate) return ''
  if (plateType === 'foreign') return String(plate).trim()
  return formatRuPlate(plate)
}

function formatMileage(value) {
  const num = Number(String(value).replace(/\s/g, ''))
  if (!Number.isFinite(num) || num <= 0) return null
  return `${num.toLocaleString('ru-RU')} км`
}

function carLabel(car) {
  return [car.brand, car.model].filter(Boolean).join(' ').trim()
}

function buildMaintenance(mileage, existing = []) {
  const mileageLabel = formatMileage(mileage)
  const rest = existing.filter(item => item.label !== 'Крайний пробег')
  if (!mileageLabel) return rest.length ? rest : existing
  return [{ label: 'Крайний пробег', value: mileageLabel }, ...rest]
}

function normalizeCarPayload(payload, previous = {}) {
  const brand = String(payload.brand || '').trim()
  const model = String(payload.model || '').trim()
  const plateType = payload.plateType || previous.plateType || 'ru'
  const plate = formatPlateDisplay(payload.plate, plateType)
  const yearRaw = String(payload.year ?? '').trim()
  const year = yearRaw ? Number(yearRaw) : null
  const mileageRaw = String(payload.mileage ?? '').replace(/\s/g, '')
  const mileage = mileageRaw ? Number(mileageRaw) : null

  return {
    brand,
    model,
    plateType,
    plate,
    vin: String(payload.vin || '').trim(),
    year: Number.isFinite(year) ? year : null,
    color: String(payload.color || '').trim(),
    mileage: Number.isFinite(mileage) ? mileage : null
  }
}

const mockCars = [
  {
    id: 'car-1',
    brand: 'Toyota',
    model: 'Camry',
    year: 2019,
    color: 'Белый',
    plate: 'А 123 ВС 116',
    plateType: 'ru',
    vin: '12345678912345678',
    mileage: 66000,
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
      status: 'booked',
      bookedAt: '14 июля 2026 · 15:00',
      master: 'Кузнецов Д.'
    }
  },
  {
    id: 'car-2',
    brand: 'Kia',
    model: 'Rio',
    year: 2021,
    color: 'Серый',
    plate: 'В 456 ОР 116',
    plateType: 'ru',
    vin: '98765432109876543',
    mileage: 42500,
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
      status: 'in_progress',
      bookedAt: '2 июня 2026 · 11:00',
      master: 'Иванов А.'
    }
  },
  {
    id: 'car-3',
    brand: 'Hyundai',
    model: 'Solaris',
    year: 2020,
    color: 'Чёрный',
    plate: 'Е 789 КХ 116',
    plateType: 'ru',
    vin: '11223344556677889',
    mileage: 58200,
    nextAppointment: {
      serviceName: 'ПАПИН ГАРАЖ',
      datetime: '12 августа 10:00',
      service: 'Ремонт тормозов',
      master: 'Кузнецов Сергей',
      car: 'Hyundai Solaris'
    },
    maintenance: [
      { label: 'Крайний пробег', value: '58 200 км' },
      { label: 'Масло', value: 'замена на 70 000' },
      { label: 'ТО', value: 'рекомендовано на 80 000' }
    ],
    repair: {
      orderNumber: '022',
      carLabel: 'Hyundai Solaris',
      status: 'needs_approval',
      bookedAt: '8 июля 2026 · 12:30',
      master: 'Кузнецов Д.'
    }
  },
  {
    id: 'car-4',
    brand: 'Volkswagen',
    model: 'Polo',
    year: 2018,
    color: 'Синий',
    plate: 'М 321 ТУ 116',
    plateType: 'ru',
    vin: '55667788990011223',
    mileage: 91400,
    nextAppointment: null,
    maintenance: [
      { label: 'Крайний пробег', value: '91 400 км' },
      { label: 'Масло', value: 'замена на 100 000' },
      { label: 'ТО', value: 'рекомендовано на 105 000' }
    ],
    repair: {
      orderNumber: '031',
      carLabel: 'Volkswagen Polo',
      status: 'ready',
      bookedAt: '20 июня 2026 · 09:00',
      master: 'Лобанов С.'
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
  },

  async get(id) {
    if (USE_MOCK) {
      const car = mockCars.find(item => item.id === id) || null
      return mockOk(car)
    }
    return http.get(`/cars/${id}`)
  },

  async create(payload) {
    if (USE_MOCK) {
      const data = normalizeCarPayload(payload)
      const car = {
        id: `car-${Date.now()}`,
        ...data,
        nextAppointment: null,
        maintenance: buildMaintenance(data.mileage, [
          { label: 'Масло', value: '—' },
          { label: 'ТО', value: '—' }
        ]),
        repair: null
      }
      mockCars.push(car)
      return mockOk(car)
    }
    return http.post('/cars', normalizeCarPayload(payload))
  },

  async update(id, payload) {
    if (USE_MOCK) {
      const index = mockCars.findIndex(item => item.id === id)
      if (index === -1) return mockOk(null)
      const previous = mockCars[index]
      const data = normalizeCarPayload(payload, previous)
      const label = carLabel(data)
      const car = {
        ...previous,
        ...data,
        maintenance: buildMaintenance(data.mileage, previous.maintenance),
        nextAppointment: previous.nextAppointment
          ? { ...previous.nextAppointment, car: label || previous.nextAppointment.car }
          : null,
        repair: previous.repair
          ? { ...previous.repair, carLabel: label || previous.repair.carLabel }
          : null
      }
      mockCars[index] = car
      return mockOk(car)
    }
    return http.put(`/cars/${id}`, normalizeCarPayload(payload))
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
    return http.get('/client-portal/ui/history', { params })
  },

  async document(orderId) {
    if (USE_MOCK) return null
    return http.raw(`/client-portal/ui/history/${orderId}/document`)
  }
}
