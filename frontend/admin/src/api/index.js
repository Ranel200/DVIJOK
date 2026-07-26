// Фасад доменных сервисов. Сейчас все методы возвращают моки.
// Когда появится бэкенд — заменяем тело методов на вызовы http.* (импорт уже готов).

import { http, USE_MOCK } from '@dvijok/shared/api/http.js'
import { mockOk, mockReject } from '@dvijok/shared/api/mock.js'

const mockUsers = [
  {
    id: 1,
    name: 'Михайлов Артем Сергеевич',
    role: 'Владелец',
    email: 'admin',
    password: 'admin'
  }
]
let mockUserIdSeq = 2

const MOCK_SESSION_KEY = 'dvijok_admin_mock_session'

function readMockSession() {
  try {
    const raw = localStorage.getItem(MOCK_SESSION_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object') return null
    return parsed
  } catch {
    return null
  }
}

function writeMockSession(session) {
  try {
    localStorage.setItem(MOCK_SESSION_KEY, JSON.stringify(session))
  } catch {}
}

function clearMockSession() {
  try {
    localStorage.removeItem(MOCK_SESSION_KEY)
  } catch {}
}

let currentUserId = null

function issueToken(user) {
  currentUserId = user.id
  const token = `mock-token-${user.id}-${Date.now()}`
  writeMockSession({ userId: user.id, token })
  return token
}

function publicUser(user) {
  const { password: _password, ...rest } = user
  return rest
}

export const authApi = {
  async login({ email, password }) {
    if (USE_MOCK) {
      const user = mockUsers.find(u => u.email === email)
      if (!user || user.password !== password) {
        return mockReject(401, { message: 'Неверный email или пароль' })
      }
      const token = issueToken(user)
      return mockOk({ token, user: publicUser(user) })
    }
    return http.post('/auth/login', { email, password })
  },

  async register(payload) {
    if (USE_MOCK) {
      const email = payload.email
      if (mockUsers.some(u => u.email === email)) {
        return mockReject(409, { message: 'Пользователь с таким email уже существует' })
      }
      const user = {
        id: mockUserIdSeq++,
        name: payload.contactName || payload.headName || 'Автосервис',
        role: mockUsers[0].role,
        email,
        password: payload.password
      }
      mockUsers.push(user)
      const token = issueToken(user)
      return mockOk({ token, user: publicUser(user) })
    }
    return http.post('/auth/register', payload)
  },

  async logout() {
    if (USE_MOCK) {
      currentUserId = null
      clearMockSession()
      return mockOk({ success: true })
    }
    return http.post('/auth/logout')
  },

  async restoreSession() {
    if (USE_MOCK) {
      const session = readMockSession()
      if (!session || session.userId == null) {
        return mockReject(401, { message: 'Не авторизован' })
      }
      const user = mockUsers.find(u => u.id === session.userId)
      if (!user) {
        clearMockSession()
        currentUserId = null
        return mockReject(401, { message: 'Не авторизован' })
      }
      currentUserId = user.id
      return mockOk({ token: session.token, user: publicUser(user) })
    }
    const user = await http.get('/auth/me')
    return { user }
  },

  async me() {
    if (USE_MOCK) {
      if (currentUserId == null) {
        return mockReject(401, { message: 'Не авторизован' })
      }
      const user = mockUsers.find(u => u.id === currentUserId)
      if (!user) {
        return mockReject(401, { message: 'Не авторизован' })
      }
      return mockOk(publicUser(user))
    }
    return http.get('/auth/me')
  }
}

export const scheduleApi = {
  async list(params) {
    if (USE_MOCK) return mockOk([])
    return http.get('/schedule', { params })
  }
}

export const crmApi = {
  async listClients(params) {
    if (USE_MOCK) return mockOk([])
    return http.get('/crm/clients', { params })
  }
}

const mockServices = [
  {
    id: 1,
    title: 'Замена масла',
    description:
      'Полная замена моторного масла с заменой масляного фильтра, проверка уровня технических жидкостей и осмотр двигателя',
    master: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' },
    price: 3500,
    priceNote: 'от 2 500 ₽',
    durationHours: 1,
    ordersCount: 47,
    status: 'active'
  },
  {
    id: 2,
    title: 'Диагностика ходовой части',
    description:
      'Проверка состояния подвески, амортизаторов, рулевых тяг и шаровых опор на предмет износа и люфтов на подъёмнике',
    master: { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' },
    price: 2500,
    priceNote: 'от 2 000 ₽',
    durationHours: 2,
    ordersCount: 31,
    status: 'active'
  },
  {
    id: 3,
    title: 'Замена тормозных колодок',
    description:
      'Демонтаж старых и установка новых передних тормозных колодок, проверка состояния тормозных дисков и суппортов',
    master: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' },
    price: 4800,
    priceNote: 'от 4 000 ₽',
    durationHours: 2,
    ordersCount: 22,
    status: 'active'
  },
  {
    id: 4,
    title: 'Регулировка развал-схождения',
    description:
      'Регулировка углов установки колёс на стенде, проверка схождения и развала по техническим нормам завода-изготовителя',
    master: { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' },
    price: 3200,
    priceNote: 'от 2 800 ₽',
    durationHours: 1,
    ordersCount: 18,
    status: 'hidden'
  },
  {
    id: 5,
    title: 'Ремонт выхлопной системы',
    description:
      'Сварка и восстановление повреждённого участка выхлопной трубы, замена резонатора и прокладок соединений',
    master: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' },
    price: 7500,
    priceNote: 'от 5 000 ₽',
    durationHours: 4,
    ordersCount: 9,
    status: 'active'
  },
  {
    id: 6,
    title: 'Замена свечей зажигания',
    description:
      'Демонтаж и установка новых свечей зажигания, проверка состояния высоковольтных проводов и катушек зажигания',
    master: { id: 5, name: 'Смирнов Дмитрий Олегович', role: 'Администратор' },
    price: 1800,
    priceNote: 'от 1 500 ₽',
    durationHours: 1,
    ordersCount: 14,
    status: 'hidden'
  },
  {
    id: 7,
    title: 'Покраска бампера',
    description:
      'Подготовка поверхности, нанесение грунта и лакокрасочного покрытия в цвет кузова, финальная полировка и сушка',
    master: { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' },
    price: 15000,
    priceNote: 'от 12 000 ₽',
    durationHours: 8,
    ordersCount: 5,
    status: 'active'
  },
  {
    id: 8,
    title: 'Шиномонтаж и балансировка',
    description:
      'Снятие и установка колёс, монтаж шин, балансировка на станке, проверка давления и состояния вентилей',
    master: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' },
    price: 2200,
    priceNote: 'от 1 800 ₽',
    durationHours: 1,
    ordersCount: 38,
    status: 'active'
  }
]

function buildServicesSummary(services) {
  const totalServices = services.length
  const priceSum = services.reduce((sum, service) => sum + service.price, 0)
  const averageCheck = totalServices ? Math.round(priceSum / totalServices) : 0
  const popular = services.reduce((best, service) => {
    if (!best || service.ordersCount > best.ordersCount) return service
    return best
  }, null)
  const revenuePerMonth = services.reduce(
    (sum, service) => sum + service.price * service.ordersCount,
    0
  )
  const activeMasters = new Set(
    services.filter(service => service.status === 'active').map(service => service.master.id)
  ).size

  return {
    totalServices,
    averageCheck,
    popularService: popular ? { name: popular.title, ordersPerMonth: popular.ordersCount } : null,
    revenuePerMonth,
    activeMasters
  }
}

export const servicesApi = {
  async list(params) {
    if (USE_MOCK) return mockOk(mockServices.map(service => ({ ...service })))
    return http.get('/services', { params })
  },

  async summary() {
    if (USE_MOCK) return mockOk(buildServicesSummary(mockServices))
    return http.get('/services/summary')
  }
}

export const tasksApi = {
  async summary() {
    if (USE_MOCK) {
      return mockOk({
        today: { count: 12, overdue: 3 },
        planned: 28,
        donePerWeek: 45
      })
    }
    return http.get('/tasks/summary')
  },

  async employees() {
    if (USE_MOCK) {
      return mockOk([
        { id: 1, name: 'Михайлов Артем Сергеевич', role: 'Владелец' },
        { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' },
        { id: 3, name: 'Сидоров Алексей Николаевич', role: 'Менеджер' },
        { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' },
        { id: 5, name: 'Смирнов Дмитрий Олегович', role: 'Администратор' }
      ])
    }
    return http.get('/tasks/employees')
  },

  async list() {
    if (USE_MOCK) {
      return mockOk([
        {
          id: 1,
          title: 'Замена масла',
          description:
            'Полная замена моторного масла с заменой масляного фильтра, проверка уровня технических жидкостей и осмотр двигателя на предмет утечек',
          status: 'new',
          deadline: '2026-07-26',
          employee: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' }
        },
        {
          id: 2,
          title: 'Диагностика ходовой части',
          description:
            'Проверка состояния подвески, амортизаторов, рулевых тяг и шаровых опор на предмет износа и люфтов на подъёмнике',
          status: 'hot',
          deadline: '2026-07-27',
          employee: { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' }
        },
        {
          id: 3,
          title: 'Замена тормозных колодок',
          description:
            'Демонтаж старых и установка новых передних тормозных колодок, проверка состояния тормозных дисков и суппортов',
          status: 'burned',
          deadline: '2026-07-20',
          employee: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' }
        },
        {
          id: 4,
          title: 'Регулировка развал-схождения',
          description:
            'Регулировка углов установки колёс на стенде, проверка схождения и развала по техническим нормам завода-изготовителя',
          status: 'done',
          deadline: '2026-07-22',
          employee: { id: 4, name: 'Кузнецова Мария Андреевна', role: 'Мастер' }
        },
        {
          id: 5,
          title: 'Ремонт выхлопной системы',
          description:
            'Сварка и восстановление повреждённого участка выхлопной трубы, замена резонатора и прокладок соединений',
          status: 'new',
          deadline: '2026-07-29',
          employee: { id: 3, name: 'Сидоров Алексей Николаевич', role: 'Менеджер' }
        },
        {
          id: 6,
          title: 'Замена свечей зажигания',
          description:
            'Демонтаж и установка новых свечей зажигания, проверка состояния высоковольтных проводов и катушек зажигания',
          status: 'hot',
          deadline: '2026-07-28',
          employee: { id: 5, name: 'Смирнов Дмитрий Олегович', role: 'Администратор' }
        },
        {
          id: 7,
          title: 'Покраска бампера',
          description:
            'Подготовка поверхности, нанесение грунта и лакокрасочного покрытия в цвет кузова, финальная полировка и сушка',
          status: 'done',
          deadline: '2026-07-21',
          employee: { id: 2, name: 'Петров Иван Сергеевич', role: 'Мастер' }
        }
      ])
    }
    return http.get('/tasks')
  },

  async create(payload) {
    if (USE_MOCK) {
      return mockOk({
        id: Date.now(),
        title: payload.title,
        description: payload.description || '',
        status: payload.status || 'new',
        deadline: payload.deadline || '',
        employee: payload.employee
      })
    }
    return http.post('/tasks', payload)
  }
}

export const settingsApi = {
  async get() {
    if (USE_MOCK) {
      return mockOk({
        service: {
          name: 'Автосервис «Движок»',
          headName: 'Иванов Алексей Петрович',
          legalType: 'ООО',
          taxSystem: 'УСН',
          inn: '7701234567',
          ogrn: '1027700132195',
          phone: '+7 495 123 45 67',
          email: 'service@dvijok.ru',
          address: 'г. Москва, ул. Автозаводская, д. 12',
          logo: '',
          description:
            'Полный спектр услуг по ремонту и обслуживанию легковых автомобилей. Диагностика, кузовной ремонт, шиномонтаж и замена масла.'
        },
        subscription: {
          status: 'active',
          plan: 'PRO',
          activeUntil: '2026-12-31',
          daysLeft: 158,
          usedMonths: 4,
          totalMonths: 12,
          features: [
            { icon: 'plane', label: 'Неограниченные заказы' },
            { icon: 'analytic', label: 'Аналитика и отчеты' },
            { icon: 'group', label: 'До 10 мастеров' },
            { icon: 'support', label: 'Поддержка 24/7' }
          ]
        },
        security: {
          currentPassword: 'dvijok-demo',
          passwordChangedAt: '2026-04-17',
          emailConfirmEnabled: true,
          email: 'service@dvijok.ru',
          phoneConfirmEnabled: false,
          phone: '+7 495 123 45 67',
          sessions: [
            {
              id: 's1',
              current: true,
              type: 'pc',
              deviceName: '',
              browser: '',
              city: 'Москва',
              country: 'Россия',
              ip: '185.12.45.78',
              lastActiveAt: ''
            },
            {
              id: 's2',
              current: false,
              type: 'pc',
              deviceName: 'Windows Desktop',
              browser: 'Edge',
              city: 'Казань',
              country: 'Россия',
              ip: '91.214.18.33',
              lastActiveAt: '2026-07-25T11:40:00'
            },
            {
              id: 's3',
              current: false,
              type: 'phone',
              deviceName: 'iPhone 15',
              browser: 'Safari',
              city: 'Санкт-Петербург',
              country: 'Россия',
              ip: '46.188.102.14',
              lastActiveAt: '2026-07-24T09:05:00'
            },
            {
              id: 's4',
              current: false,
              type: 'laptop',
              deviceName: 'ThinkPad X1',
              browser: 'Firefox',
              city: 'Новосибирск',
              country: 'Россия',
              ip: '178.44.112.9',
              lastActiveAt: '2026-07-20T16:22:00'
            }
          ],
          loginHistory: [
            {
              id: 'h1',
              success: true,
              deviceName: 'MacBook Pro 14',
              browser: 'Chrome',
              city: 'Москва',
              country: 'Россия',
              ip: '185.12.45.78',
              loggedAt: '2026-07-26T20:15:00'
            },
            {
              id: 'h2',
              success: false,
              deviceName: 'Unknown Device',
              browser: 'Chrome',
              city: 'Минск',
              country: 'Беларусь',
              ip: '93.125.44.12',
              loggedAt: '2026-07-26T14:02:00'
            },
            {
              id: 'h3',
              success: true,
              deviceName: 'Windows Desktop',
              browser: 'Edge',
              city: 'Казань',
              country: 'Россия',
              ip: '91.214.18.33',
              loggedAt: '2026-07-25T11:40:00'
            },
            {
              id: 'h4',
              success: true,
              deviceName: 'iPhone 15',
              browser: 'Safari',
              city: 'Санкт-Петербург',
              country: 'Россия',
              ip: '46.188.102.14',
              loggedAt: '2026-07-24T09:05:00'
            },
            {
              id: 'h5',
              success: false,
              deviceName: 'Android Phone',
              browser: 'Chrome',
              city: 'Алматы',
              country: 'Казахстан',
              ip: '87.255.210.67',
              loggedAt: '2026-07-22T22:18:00'
            }
          ]
        }
      })
    }
    return http.get('/settings')
  },

  async update(payload) {
    if (USE_MOCK) return mockOk(payload)
    return http.put('/settings', payload)
  }
}
