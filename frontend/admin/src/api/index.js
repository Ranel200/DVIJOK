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

export const servicesApi = {
  async list(params) {
    if (USE_MOCK) return mockOk([])
    return http.get('/services', { params })
  },

  async summary() {
    if (USE_MOCK) {
      return mockOk({
        totalServices: 24,
        averageCheck: 1500,
        popularService: { name: 'Замена масла', ordersPerMonth: 47 },
        revenuePerMonth: 287500,
        activeMasters: 8
      })
    }
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
  }
}

export const settingsApi = {
  async get() {
    if (USE_MOCK) return mockOk({})
    return http.get('/settings')
  },

  async update(payload) {
    if (USE_MOCK) return mockOk(payload)
    return http.put('/settings', payload)
  }
}
