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

let currentUserId = null

function issueToken(user) {
  currentUserId = user.id
  return `mock-token-${user.id}-${Date.now()}`
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
      return mockOk({ success: true })
    }
    return http.post('/auth/logout')
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
