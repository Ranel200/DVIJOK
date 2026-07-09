// Фасад доменных сервисов. Сейчас все методы возвращают моки.
// Когда появится бэкенд — заменяем тело методов на вызовы http.* (импорт уже готов).

import { http, USE_MOCK } from './http.js'
import { mockOk } from './mock.js'

export const authApi = {
  async login({ email }) {
    if (USE_MOCK) {
      return mockOk({
        token: 'mock-token',
        user: { id: 1, name: 'Администратор', email }
      })
    }
    return http.post('/auth/login', { email })
  },

  async logout() {
    if (USE_MOCK) return mockOk({ success: true })
    return http.post('/auth/logout')
  },

  async me() {
    if (USE_MOCK)
      return mockOk({
        id: 1,
        name: 'Администратор',
        email: 'admin@dvijok.local'
      })
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
