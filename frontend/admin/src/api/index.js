// Фасад доменных сервисов. Сейчас все методы возвращают моки.
// Когда появится бэкенд — заменяем тело методов на вызовы http.* (импорт уже готов).

import { http, USE_MOCK } from '@dvijok/shared/api/http.js'
import { mockOk, mockReject } from '@dvijok/shared/api/mock.js'
import { STAFF_ROLE_LABELS, mapLegacyRole } from '@/constants/staff.js'
import { startOfWeek } from '@/utils/formatDateRu.js'

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

const mockEmployees = [
  {
    id: 1,
    name: 'Михайлов Артем Сергеевич',
    role: 'Владелец',
    avatarBg: '#5C6BC0',
    workDays: [1, 2, 3, 4, 5],
    start: '09:00',
    end: '18:00'
  },
  {
    id: 2,
    name: 'Петров Иван Сергеевич',
    role: 'Мастер',
    avatarBg: '#43A047',
    workDays: [1, 2, 3, 4, 5],
    start: '09:00',
    end: '18:00'
  },
  {
    id: 3,
    name: 'Сидоров Алексей Николаевич',
    role: 'Менеджер',
    avatarBg: '#FB8C00',
    workDays: [1, 2, 3, 4, 5, 6],
    start: '10:00',
    end: '19:00'
  },
  {
    id: 4,
    name: 'Кузнецова Мария Андреевна',
    role: 'Мастер',
    avatarBg: '#EC407A',
    workDays: [2, 3, 4, 5, 6],
    start: '11:00',
    end: '20:00'
  },
  {
    id: 5,
    name: 'Смирнов Дмитрий Олегович',
    role: 'Администратор',
    avatarBg: '#039BE5',
    workDays: [1, 2, 3, 4, 5],
    start: '08:00',
    end: '17:00'
  },
  {
    id: 6,
    name: 'Кузнецов Вячеслав Сергеевич',
    role: 'Мастер',
    avatarBg: '#5C6BC0',
    workDays: [1, 2, 3, 4, 5],
    start: '10:00',
    end: '20:00'
  },
  {
    id: 7,
    name: 'Васильева Анна Игоревна',
    role: 'Мастер',
    avatarBg: '#8E24AA',
    workDays: [1, 2, 3, 4, 5],
    start: '10:00',
    end: '19:00'
  },
  {
    id: 8,
    name: 'Новиков Павел Викторович',
    role: 'Мастер',
    avatarBg: '#00897B',
    workDays: [1, 3, 5],
    start: '12:00',
    end: '21:00'
  },
  {
    id: 9,
    name: 'Морозова Елена Сергеевна',
    role: 'Менеджер',
    avatarBg: '#F4511E',
    workDays: [1, 2, 3, 4, 5],
    start: '09:00',
    end: '18:00'
  },
  {
    id: 10,
    name: 'Волков Андрей Петрович',
    role: 'Мастер',
    avatarBg: '#3949AB',
    workDays: [2, 3, 4, 5, 6],
    start: '10:00',
    end: '20:00'
  },
  {
    id: 11,
    name: 'Соколова Ирина Алексеевна',
    role: 'Администратор',
    avatarBg: '#7B1FA2',
    workDays: [1, 2, 3, 4, 5, 6],
    start: '08:00',
    end: '16:00'
  },
  {
    id: 12,
    name: 'Лебедев Никита Романович',
    role: 'Мастер',
    avatarBg: '#2E7D32',
    workDays: [1, 2, 4, 5],
    start: '11:00',
    end: '20:00'
  },
  {
    id: 13,
    name: 'Козлова Татьяна Владимировна',
    role: 'Мастер',
    avatarBg: '#C62828',
    workDays: [1, 2, 3, 4, 5],
    start: '09:00',
    end: '17:00'
  },
  {
    id: 14,
    name: 'Орлов Максим Денисович',
    role: 'Менеджер',
    avatarBg: '#0277BD',
    workDays: [1, 2, 3, 4, 5],
    start: '10:00',
    end: '19:00'
  },
  {
    id: 15,
    name: 'Павлова Ольга Николаевна',
    role: 'Мастер',
    avatarBg: '#6A1B9A',
    workDays: [3, 4, 5, 6, 0],
    start: '12:00',
    end: '21:00'
  },
  {
    id: 16,
    name: 'Григорьев Сергей Иванович',
    role: 'Мастер',
    avatarBg: '#00695C',
    workDays: [1, 2, 3, 4, 5],
    start: '08:00',
    end: '17:00'
  }
]

function mockEmployeeBrief(id) {
  const employee = mockEmployees.find(item => item.id === id)
  if (!employee) return null
  return { id: employee.id, name: employee.name, role: employee.role }
}

function emptyStaffAccess() {
  return {
    schedule: false,
    crm: false,
    services: false,
    tasks: false,
    qr: false,
    settings: false
  }
}

function emptyStaffDocuments() {
  return { passport: null, inn: null, medicalBook: null }
}

function toEmployeeDetail(staff) {
  return {
    id: staff.id,
    name: staff.name,
    role: staff.role,
    roleKey: staff.roleKey || mapLegacyRole(staff.role),
    phone: staff.phone || '',
    email: staff.email || '',
    duties: staff.duties || '',
    rate: staff.rate ?? null,
    color: staff.color || staff.avatarBg || '',
    avatarBg: staff.avatarBg,
    documents: {
      ...emptyStaffDocuments(),
      ...staff.documents
    },
    access: {
      ...emptyStaffAccess(),
      ...staff.access
    },
    login: staff.login || '',
    password: staff.password || ''
  }
}

function applyEmployeePayload(staff, payload) {
  const roleKey = payload.role || staff.roleKey || mapLegacyRole(staff.role)
  staff.name = payload.name || staff.name
  staff.roleKey = roleKey
  staff.role = STAFF_ROLE_LABELS[roleKey] || staff.role
  staff.phone = payload.phone || ''
  staff.email = payload.email || ''
  staff.duties = payload.duties || ''
  staff.rate = payload.rate ?? null
  staff.color = payload.color || staff.color || staff.avatarBg
  staff.avatarBg = payload.color || staff.avatarBg
  staff.documents = {
    ...emptyStaffDocuments(),
    ...(payload.documents || staff.documents)
  }
  staff.access = {
    ...emptyStaffAccess(),
    ...(payload.access || staff.access)
  }
  if (payload.login !== undefined) staff.login = payload.login || ''
  if (payload.password !== undefined) staff.password = payload.password || ''
}

function parseTimeToHours(value) {
  const [h, m] = String(value || '0:0')
    .split(':')
    .map(Number)
  return (h || 0) + (m || 0) / 60
}

function buildStaffMonthDays(staff, year, month) {
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days = []
  let totalDays = 0
  let totalHours = 0

  for (let day = 1; day <= daysInMonth; day++) {
    const weekday = new Date(year, month, day).getDay()
    const active = staff.workDays.includes(weekday)
    if (active) {
      const hours = parseTimeToHours(staff.end) - parseTimeToHours(staff.start)
      totalDays += 1
      totalHours += hours
      days.push({ day, active: true, start: staff.start, end: staff.end })
    } else {
      days.push({ day, active: false, start: null, end: null })
    }
  }

  return {
    id: staff.id,
    name: staff.name,
    role: staff.role,
    avatarBg: staff.avatarBg,
    totalDays,
    totalHours: Math.round(totalHours),
    days
  }
}

const MOCK_BOOKINGS = [
  {
    brand: 'TOYOTA',
    plate: 'А 123 ВС 116',
    clientName: 'Иванов Пётр',
    serviceName: 'Замена масла'
  },
  { brand: 'BMW', plate: 'К 456 МН 116', clientName: 'Сидоров Олег', serviceName: 'Диагностика' },
  {
    brand: 'KIA',
    plate: 'Е 789 ОР 116',
    clientName: 'Кузнецова Анна',
    serviceName: 'Шиномонтаж'
  },
  {
    brand: 'HYUNDAI',
    plate: 'М 012 СТ 116',
    clientName: 'Петрова Мария',
    serviceName: 'ТО-2'
  },
  {
    brand: 'LADA',
    plate: 'Х 000 ХХ 116',
    clientName: 'Новиков Павел',
    serviceName: 'Ремонт ходовой'
  },
  {
    brand: 'AUDI',
    plate: 'В 321 УК 116',
    clientName: 'Морозов Игорь',
    serviceName: 'Покраска'
  }
]

function formatHourLabel(hour) {
  return `${String(hour).padStart(2, '0')}:00`
}

function buildCalendarWeek(weekStartIso) {
  const start = new Date(`${weekStartIso}T00:00:00`)
  const masters = mockEmployees.filter(item => item.role === 'Мастер').slice(0, 5)

  let minHour = 24
  let maxHour = 0
  for (const staff of masters) {
    minHour = Math.min(minHour, Math.floor(parseTimeToHours(staff.start)))
    maxHour = Math.max(maxHour, Math.ceil(parseTimeToHours(staff.end)))
  }
  if (minHour >= maxHour) {
    minHour = 9
    maxHour = 18
  }

  const times = []
  for (let hour = minHour; hour < maxHour; hour++) {
    times.push(formatHourLabel(hour))
  }

  const weekDates = Array.from({ length: 7 }, (_, offset) => {
    const date = new Date(start)
    date.setDate(start.getDate() + offset)
    return {
      offset,
      weekday: date.getDay(),
      dateKey: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }
  })

  const daySlots = weekDates.map(() => Object.fromEntries(times.map(time => [time, []])))

  for (const time of times) {
    const hour = parseTimeToHours(time)
    // 1–3 сотрудника на слот, не все сразу
    const count = 1 + (hour % 3)
    const shift = hour % masters.length
    const selected = Array.from(
      { length: count },
      (_, i) => masters[(shift + i * 2) % masters.length]
    )

    for (const staff of selected) {
      const blocksByDay = weekDates.map(({ offset, weekday, dateKey }) => {
        const worksDay = staff.workDays.includes(weekday)
        const inHours = hour >= parseTimeToHours(staff.start) && hour < parseTimeToHours(staff.end)

        if (!worksDay || !inHours) {
          return {
            id: `${staff.id}-${dateKey}-${time}-lock`,
            employeeId: staff.id,
            employeeName: staff.name,
            color: staff.avatarBg,
            status: 'unavailable'
          }
        }

        const seed = staff.id * 31 + offset * 17 + hour * 13
        const kind = seed % 4
        if (kind === 0) {
          return {
            id: `${staff.id}-${dateKey}-${time}-free`,
            employeeId: staff.id,
            employeeName: staff.name,
            color: staff.avatarBg,
            status: 'available'
          }
        }

        const booking = MOCK_BOOKINGS[seed % MOCK_BOOKINGS.length]
        return {
          id: `${staff.id}-${dateKey}-${time}-busy`,
          employeeId: staff.id,
          employeeName: staff.name,
          color: staff.avatarBg,
          status: 'busy',
          brand: booking.brand,
          plate: booking.plate,
          clientName: booking.clientName,
          serviceName: booking.serviceName
        }
      })

      // ряд только если есть хотя бы один доступный/занятый день
      if (blocksByDay.every(block => block.status === 'unavailable')) continue

      blocksByDay.forEach((block, dayIndex) => {
        daySlots[dayIndex][time].push(block)
      })
    }
  }

  return {
    times,
    days: weekDates.map((day, index) => ({
      date: day.dateKey,
      slots: daySlots[index]
    }))
  }
}

export const scheduleApi = {
  async list(params) {
    if (USE_MOCK) return mockOk([])
    return http.get('/schedule', { params })
  },

  async calendar(params = {}) {
    if (USE_MOCK) {
      const monday = startOfWeek(new Date())
      const weekStart =
        params.weekStart ||
        `${monday.getFullYear()}-${String(monday.getMonth() + 1).padStart(2, '0')}-${String(monday.getDate()).padStart(2, '0')}`
      return mockOk(buildCalendarWeek(weekStart))
    }
    return http.get('/schedule/calendar', { params })
  },

  async employees(params = {}) {
    if (USE_MOCK) {
      const now = new Date()
      const year = params.year ?? now.getFullYear()
      const month = params.month ?? now.getMonth()
      return mockOk(mockEmployees.map(staff => buildStaffMonthDays(staff, year, month)))
    }
    return http.get('/schedule/employees', { params })
  },

  async removeEmployee(id) {
    if (USE_MOCK) {
      const index = mockEmployees.findIndex(item => item.id === id)
      if (index === -1) return mockReject(404, { message: 'Сотрудник не найден' })
      mockEmployees.splice(index, 1)
      return mockOk(null)
    }
    return http.delete(`/schedule/employees/${id}`)
  },

  async getEmployee(id) {
    if (USE_MOCK) {
      const employee = mockEmployees.find(item => item.id === id)
      if (!employee) return mockReject(404, { message: 'Сотрудник не найден' })
      if (!employee.documents) {
        employee.documents = {
          passport: { name: 'passport.pdf', fileName: 'passport.pdf' },
          inn: { name: 'inn.pdf', fileName: 'inn.pdf' },
          medicalBook: null
        }
      }
      if (!employee.access) {
        employee.access = {
          schedule: true,
          crm: true,
          services: true,
          tasks: true,
          qr: false,
          settings: false
        }
      }
      return mockOk(toEmployeeDetail(employee))
    }
    return http.get(`/schedule/employees/${id}`)
  },

  async createEmployee(payload) {
    if (USE_MOCK) {
      const nextId = mockEmployees.reduce((max, item) => Math.max(max, item.id), 0) + 1
      const roleKey = payload.role || 'senior_admin'
      const employee = {
        id: nextId,
        name: payload.name || '',
        roleKey,
        role: STAFF_ROLE_LABELS[roleKey] || 'Сотрудник',
        avatarBg: payload.color || '#5C6BC0',
        color: payload.color || '#5C6BC0',
        phone: payload.phone || '',
        email: payload.email || '',
        duties: payload.duties || '',
        rate: payload.rate ?? null,
        documents: {
          ...emptyStaffDocuments(),
          ...payload.documents
        },
        access: {
          ...emptyStaffAccess(),
          ...payload.access
        },
        login: payload.login || '',
        password: payload.password || '',
        workDays: [1, 2, 3, 4, 5],
        start: '09:00',
        end: '18:00'
      }
      mockEmployees.push(employee)
      return mockOk(toEmployeeDetail(employee))
    }
    return http.post('/schedule/employees', payload)
  },

  async updateEmployee(id, payload) {
    if (USE_MOCK) {
      const employee = mockEmployees.find(item => item.id === id)
      if (!employee) return mockReject(404, { message: 'Сотрудник не найден' })
      applyEmployeePayload(employee, payload)
      return mockOk(toEmployeeDetail(employee))
    }
    return http.put(`/schedule/employees/${id}`, payload)
  },

  async saveSettings(payload) {
    if (USE_MOCK) {
      const targets =
        payload.employeeId === 'all'
          ? mockEmployees
          : mockEmployees.filter(item => item.id === payload.employeeId)
      for (const staff of targets) {
        staff.workDays = [...(payload.workDays || [])]
        staff.start = payload.start || staff.start
        staff.end = payload.end || staff.end
        staff.breaks = Array.isArray(payload.breaks)
          ? payload.breaks.map(item => ({ start: item.start, end: item.end }))
          : []
      }
      return mockOk(null)
    }
    return http.put('/schedule/settings', payload)
  }
}

const mockCrmColumns = [
  {
    id: 'new',
    title: 'Новая сделка',
    gradient: 'linear-gradient(94.25deg, #0031B1 11.54%, #02167F 100%)',
    items: [
      {
        id: 'n1',
        number: 1,
        amount: 23000,
        clientName: 'Иванов Пётр',
        phone: '+7 903 214 55 18',
        carBrand: 'Toyota Camry',
        plate: 'А 123 ВС 116',
        services: ['Замена масла', 'Диагностика'],
        masters: 'Смирнов Алексей, Козлов',
        createdAt: '14 июля',
        updatedAt: '17 июля'
      },
      {
        id: 'n2',
        number: 2,
        amount: 9200,
        clientName: 'Кузнецова Мария',
        phone: '+7 917 440 12 03',
        carBrand: 'Kia Rio',
        plate: 'К 451 МН 116',
        services: ['Шиномонтаж'],
        masters: 'Петров Иван',
        createdAt: '18 июля',
        updatedAt: '18 июля'
      }
    ]
  },
  {
    id: 'primary',
    title: 'Первичная запись',
    gradient: 'linear-gradient(94.25deg, #007CB1 11.54%, #02517F 100%)',
    items: [
      {
        id: 'p1',
        number: 3,
        amount: 12400,
        clientName: 'Соколов Олег',
        phone: '+7 987 301 66 42',
        carBrand: 'Hyundai Solaris',
        plate: 'Е 782 ОР 116',
        services: ['ТО-1', 'Замена фильтров'],
        masters: 'Орлов Дмитрий, Волков',
        createdAt: '12 июля',
        updatedAt: '15 июля'
      }
    ]
  },
  {
    id: 'diagnostics',
    title: 'Диагностика',
    gradient: 'linear-gradient(94.25deg, #EA9515 0%, #D87503 100%)',
    items: [
      {
        id: 'd1',
        number: 4,
        amount: 5600,
        clientName: 'Васильева Анна',
        phone: '+7 950 118 90 27',
        carBrand: 'Volkswagen Polo',
        plate: 'М 019 ТК 116',
        services: ['Компьютерная диагностика', 'Проверка подвески'],
        masters: 'Морозов Сергей',
        createdAt: '10 июля',
        updatedAt: '16 июля'
      },
      {
        id: 'd2',
        number: 5,
        amount: 7800,
        clientName: 'Лебедев Дмитрий',
        phone: '+7 927 665 44 10',
        carBrand: 'Skoda Octavia',
        plate: 'Т 330 УХ 116',
        services: ['Диагностика двигателя'],
        masters: 'Новиков Павел, Егоров',
        createdAt: '11 июля',
        updatedAt: '17 июля'
      }
    ]
  },
  {
    id: 'approval',
    title: 'Согласование работ',
    gradient: 'linear-gradient(94.25deg, #A838DD 0%, #530097 100%)',
    items: [
      {
        id: 'a1',
        number: 6,
        amount: 45200,
        clientName: 'Никитин Сергей',
        phone: '+7 903 778 21 54',
        carBrand: 'BMW X5',
        plate: 'Х 777 КК 116',
        services: ['Замена тормозных дисков', 'Развал-схождение', 'Химчистка'],
        masters: 'Фёдоров Илья, Белов',
        createdAt: '8 июля',
        updatedAt: '19 июля'
      }
    ]
  },
  {
    id: 'secondary',
    title: 'Вторичная запись',
    gradient: 'linear-gradient(94.25deg, #007CB1 11.54%, #02517F 100%)',
    items: []
  },
  {
    id: 'in_progress',
    title: 'В работе',
    gradient: 'linear-gradient(94.25deg, #EA6415 0%, #D83803 100%)',
    items: [
      {
        id: 'w1',
        number: 7,
        amount: 21300,
        clientName: 'Романов Павел',
        phone: '+7 916 203 88 71',
        carBrand: 'Lada Vesta',
        plate: 'В 214 СН 116',
        services: ['Замена ГРМ', 'Антифриз'],
        masters: 'Семёнов Артём',
        createdAt: '5 июля',
        updatedAt: '20 июля'
      },
      {
        id: 'w2',
        number: 8,
        amount: 16750,
        clientName: 'Михайлова Елена',
        phone: '+7 999 145 03 62',
        carBrand: 'Renault Duster',
        plate: 'С 560 АЕ 116',
        services: ['Ремонт подвески', 'Замена стоек'],
        masters: 'Григорьев Никита, Павлов',
        createdAt: '6 июля',
        updatedAt: '19 июля'
      },
      {
        id: 'w3',
        number: 9,
        amount: 14200,
        clientName: 'Ковалёв Артём',
        phone: '+7 937 812 49 05',
        carBrand: 'Ford Focus',
        plate: 'О 891 РТ 116',
        services: ['Покраска бампера'],
        masters: 'Зайцев Максим',
        createdAt: '7 июля',
        updatedAt: '18 июля'
      },
      {
        id: 'w4',
        number: 10,
        amount: 28900,
        clientName: 'Степанова Наталья',
        phone: '+7 902 334 17 86',
        carBrand: 'Audi A4',
        plate: 'Р 045 ВМ 116',
        services: ['Замена сцепления', 'Диагностика АКПП'],
        masters: 'Тихонов Денис, Яковлев',
        createdAt: '4 июля',
        updatedAt: '20 июля'
      },
      {
        id: 'w5',
        number: 11,
        amount: 11500,
        clientName: 'Дмитриев Виктор',
        phone: '+7 987 650 28 39',
        carBrand: 'Chevrolet Cruze',
        plate: 'У 673 КП 116',
        services: ['Замена масла', 'Фильтр салона', 'Свечи'],
        masters: 'Андреев Роман',
        createdAt: '9 июля',
        updatedAt: '16 июля'
      },
      {
        id: 'w6',
        number: 12,
        amount: 33100,
        clientName: 'Фомина Ольга',
        phone: '+7 917 228 74 11',
        carBrand: 'Mitsubishi Outlander',
        plate: 'Н 318 ДС 116',
        services: ['Ремонт кондиционера'],
        masters: 'Борисов Егор, Макаров',
        createdAt: '3 июля',
        updatedAt: '19 июля'
      },
      {
        id: 'w7',
        number: 13,
        amount: 19800,
        clientName: 'Жуков Кирилл',
        phone: '+7 964 501 93 20',
        carBrand: 'Honda Civic',
        plate: 'Х 000 ХХ 116',
        services: ['Полировка', 'Керамика'],
        masters: 'Власов Игорь',
        createdAt: '13 июля',
        updatedAt: '17 июля'
      },
      {
        id: 'w8',
        number: 14,
        amount: 24600,
        clientName: 'Медведева Татьяна',
        phone: '+7 000 000 00 00',
        carBrand: 'Subaru Forester',
        plate: 'А 777 ТО 116',
        services: ['Замена ремня', 'Ролики', 'Помпа'],
        masters: 'Киселёв Антон, Савельев',
        createdAt: '2 июля',
        updatedAt: '20 июля'
      }
    ]
  },
  {
    id: 'waiting',
    title: 'Ожидание',
    gradient: 'linear-gradient(94.25deg, #7F38DD 0%, #410097 100%)',
    items: [
      {
        id: 'h1',
        number: 15,
        amount: 9800,
        clientName: 'Трофимов Игорь',
        phone: '+7 925 410 67 33',
        carBrand: 'Nissan Qashqai',
        plate: 'К 222 ЛМ 116',
        services: ['Ожидание запчасти'],
        masters: 'Соловьёв Юрий',
        createdAt: '1 июля',
        updatedAt: '15 июля'
      }
    ]
  },
  {
    id: 'done',
    title: 'Выдано/завершено',
    gradient: 'linear-gradient(94.25deg, #7FCB37 0%, #006D1F 100%)',
    items: [
      {
        id: 'c1',
        number: 16,
        amount: 30400,
        clientName: 'Белова Юлия',
        phone: '+7 903 156 82 49',
        carBrand: 'Mazda 6',
        plate: 'Е 909 СН 116',
        services: ['Полное ТО', 'Замена колодок'],
        masters: 'Гусев Владислав, Крылов',
        createdAt: '28 июня',
        updatedAt: '14 июля'
      }
    ]
  }
]

export const crmApi = {
  async listClients(params) {
    if (USE_MOCK) return mockOk([])
    return http.get('/crm/clients', { params })
  },

  async listColumns() {
    if (USE_MOCK) {
      const columns = mockCrmColumns.map(column => ({
        ...column,
        items: [...column.items]
      }))
      return mockOk(columns)
    }
    return http.get('/crm/columns')
  },

  async listDeals() {
    if (USE_MOCK) return mockOk(mockCrmDeals.map(deal => ({ ...deal })))
    return http.get('/crm/deals')
  },

  async createOrder(payload) {
    if (USE_MOCK) {
      const nextNumber =
        Math.max(
          0,
          ...mockCrmDeals.map(item => item.number),
          ...mockCrmColumns.flatMap(column => column.items.map(item => item.number))
        ) + 1

      const serviceTitles = (payload.lines || [])
        .map(line => mockServices.find(service => service.id === line.serviceId)?.title)
        .filter(Boolean)

      const masterNames = (payload.lines || [])
        .map(line => mockEmployees.find(employee => employee.id === line.masterId)?.name)
        .filter(Boolean)

      const amount = (payload.lines || []).reduce((sum, line) => {
        const price = Number(line.price) || 0
        const discount = Math.min(100, Math.max(0, Number(line.discount) || 0))
        return sum + Math.max(0, Math.round(price * (1 - discount / 100)))
      }, 0)

      const carBrand = [payload.brand, payload.model].filter(Boolean).join(' ').trim()
      const nowLabel = new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
      const id = `o${Date.now()}`
      const status = payload.status || 'new'

      const deal = {
        id,
        number: nextNumber,
        status,
        clientName: payload.clientName || '',
        carBrand: carBrand || '',
        carYear: payload.year ? Number(payload.year) || null : null,
        amount,
        services: serviceTitles,
        master: masterNames[0] || '',
        createdAt: nowLabel,
        updatedAt: nowLabel
      }

      mockCrmDeals.unshift(deal)

      const column =
        mockCrmColumns.find(item => item.id === status) ||
        mockCrmColumns.find(item => item.id === 'new')
      if (column) {
        column.items.unshift({
          id,
          number: nextNumber,
          amount,
          clientName: payload.clientName || '',
          phone: payload.phone || '',
          carBrand: carBrand || '',
          plate: payload.plate || '',
          services: serviceTitles,
          masters: masterNames.join(', '),
          createdAt: nowLabel,
          updatedAt: nowLabel
        })
      }

      return mockOk(deal)
    }
    return http.post('/crm/orders', payload)
  }
}

const mockCrmDeals = [
  {
    id: 'l1',
    number: 1,
    status: 'new',
    clientName: 'Иванов Пётр',
    carBrand: 'Toyota Camry',
    carYear: 2021,
    amount: 23000,
    services: ['Замена масла', 'Диагностика'],
    master: 'Смирнов Алексей',
    createdAt: '14 июля',
    updatedAt: '17 июля'
  },
  {
    id: 'l2',
    number: 2,
    status: 'new',
    clientName: 'Кузнецова Мария',
    carBrand: 'Kia Rio',
    carYear: 2019,
    amount: 9200,
    services: ['Шиномонтаж'],
    master: 'Петров Иван',
    createdAt: '18 июля',
    updatedAt: '18 июля'
  },
  {
    id: 'l3',
    number: 3,
    status: 'primary',
    clientName: 'Соколов Олег',
    carBrand: 'Hyundai Solaris',
    carYear: 2020,
    amount: 12400,
    services: ['ТО-1', 'Замена фильтров'],
    master: 'Орлов Дмитрий',
    createdAt: '12 июля',
    updatedAt: '15 июля'
  },
  {
    id: 'l4',
    number: 4,
    status: 'diagnostics',
    clientName: 'Васильева Анна',
    carBrand: 'Volkswagen Polo',
    carYear: 2019,
    amount: 5600,
    services: ['Компьютерная диагностика', 'Проверка подвески'],
    master: 'Морозов Сергей',
    createdAt: '10 июля',
    updatedAt: '16 июля'
  },
  {
    id: 'l5',
    number: 5,
    status: 'diagnostics',
    clientName: 'Лебедев Дмитрий',
    carBrand: 'Skoda Octavia',
    carYear: 2018,
    amount: 7800,
    services: ['Диагностика двигателя'],
    master: 'Новиков Павел',
    createdAt: '11 июля',
    updatedAt: '17 июля'
  },
  {
    id: 'l6',
    number: 6,
    status: 'approval',
    clientName: 'Никитин Сергей',
    carBrand: 'BMW X5',
    carYear: 2023,
    amount: 45200,
    services: ['Замена тормозных дисков', 'Развал-схождение', 'Химчистка'],
    master: 'Фёдоров Илья',
    createdAt: '8 июля',
    updatedAt: '19 июля'
  },
  {
    id: 'l7',
    number: 7,
    status: 'in_progress',
    clientName: 'Романов Павел',
    carBrand: 'Lada Vesta',
    carYear: 2022,
    amount: 21300,
    services: ['Замена ГРМ', 'Антифриз'],
    master: 'Семёнов Артём',
    createdAt: '5 июля',
    updatedAt: '20 июля'
  },
  {
    id: 'l8',
    number: 8,
    status: 'in_progress',
    clientName: 'Михайлова Елена',
    carBrand: 'Renault Duster',
    carYear: 2017,
    amount: 16750,
    services: ['Ремонт подвески', 'Замена стоек'],
    master: 'Григорьев Никита',
    createdAt: '6 июля',
    updatedAt: '19 июля'
  },
  {
    id: 'l9',
    number: 9,
    status: 'in_progress',
    clientName: 'Ковалёв Артём',
    carBrand: 'Ford Focus',
    carYear: 2018,
    amount: 14200,
    services: ['Покраска бампера'],
    master: 'Зайцев Максим',
    createdAt: '7 июля',
    updatedAt: '18 июля'
  },
  {
    id: 'l10',
    number: 10,
    status: 'waiting',
    clientName: 'Трофимов Игорь',
    carBrand: 'Nissan Qashqai',
    carYear: 2019,
    amount: 9800,
    services: ['Ожидание запчасти'],
    master: 'Соловьёв Юрий',
    createdAt: '1 июля',
    updatedAt: '15 июля'
  },
  {
    id: 'l11',
    number: 11,
    status: 'in_progress',
    clientName: 'Фомина Ольга',
    carBrand: 'Mitsubishi Outlander',
    carYear: 2019,
    amount: 33100,
    services: ['Ремонт кондиционера'],
    master: 'Борисов Егор',
    createdAt: '3 июля',
    updatedAt: '19 июля'
  },
  {
    id: 'l12',
    number: 12,
    status: 'done',
    clientName: 'Белова Юлия',
    carBrand: 'Mazda 6',
    carYear: 2021,
    amount: 30400,
    services: ['Полное ТО', 'Замена колодок'],
    master: 'Гусев Владислав',
    createdAt: '28 июня',
    updatedAt: '14 июля',
    documents: [
      {
        id: 'd1',
        color: '#B3C8FF',
        title: 'Заказ-наряд №012',
        meta: 'Mazda 6 · Гусев В. · 30 400 ₽',
        date: 'Сформирован: 14 июля 2026'
      },
      {
        id: 'd2',
        color: '#FFCCAE',
        title: 'Акт выполненных работ',
        meta: 'Полное ТО, Замена колодок · Гусев В.',
        date: 'Подписан: 14 июля 2026'
      },
      {
        id: 'd3',
        color: '#D7BCFB',
        title: 'Счет на оплату №012',
        meta: 'Итого: 30 400 ₽ · Не оплачен',
        date: 'Выставлен: 14 июля 2026'
      },
      {
        id: 'd4',
        color: '#CEFFA2',
        title: 'Гарантийный талон №012',
        meta: 'Полное ТО, Замена колодок',
        date: 'Выдан: 14 июля 2026'
      }
    ]
  }
]

const mockServices = [
  {
    id: 1,
    title: 'Замена масла',
    description:
      'Полная замена моторного масла с заменой масляного фильтра, проверка уровня технических жидкостей и осмотр двигателя',
    master: mockEmployeeBrief(2),
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
    master: mockEmployeeBrief(4),
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
    master: mockEmployeeBrief(2),
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
    master: mockEmployeeBrief(4),
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
    master: mockEmployeeBrief(2),
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
    master: mockEmployeeBrief(5),
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
    master: mockEmployeeBrief(4),
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
    master: mockEmployeeBrief(2),
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
      return mockOk(mockEmployees.map(({ id, name, role }) => ({ id, name, role })))
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
          employee: mockEmployeeBrief(2)
        },
        {
          id: 2,
          title: 'Диагностика ходовой части',
          description:
            'Проверка состояния подвески, амортизаторов, рулевых тяг и шаровых опор на предмет износа и люфтов на подъёмнике',
          status: 'hot',
          deadline: '2026-07-27',
          employee: mockEmployeeBrief(4)
        },
        {
          id: 3,
          title: 'Замена тормозных колодок',
          description:
            'Демонтаж старых и установка новых передних тормозных колодок, проверка состояния тормозных дисков и суппортов',
          status: 'burned',
          deadline: '2026-07-20',
          employee: mockEmployeeBrief(2)
        },
        {
          id: 4,
          title: 'Регулировка развал-схождения',
          description:
            'Регулировка углов установки колёс на стенде, проверка схождения и развала по техническим нормам завода-изготовителя',
          status: 'done',
          deadline: '2026-07-22',
          employee: mockEmployeeBrief(4)
        },
        {
          id: 5,
          title: 'Ремонт выхлопной системы',
          description:
            'Сварка и восстановление повреждённого участка выхлопной трубы, замена резонатора и прокладок соединений',
          status: 'new',
          deadline: '2026-07-29',
          employee: mockEmployeeBrief(3)
        },
        {
          id: 6,
          title: 'Замена свечей зажигания',
          description:
            'Демонтаж и установка новых свечей зажигания, проверка состояния высоковольтных проводов и катушек зажигания',
          status: 'hot',
          deadline: '2026-07-28',
          employee: mockEmployeeBrief(5)
        },
        {
          id: 7,
          title: 'Покраска бампера',
          description:
            'Подготовка поверхности, нанесение грунта и лакокрасочного покрытия в цвет кузова, финальная полировка и сушка',
          status: 'done',
          deadline: '2026-07-21',
          employee: mockEmployeeBrief(2)
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
          bankAccount: '40702810123456789012',
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
          securityLevel: 'weak',
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
            },
            {
              id: 'h6',
              success: true,
              deviceName: 'ThinkPad X1',
              browser: 'Firefox',
              city: 'Новосибирск',
              country: 'Россия',
              ip: '178.44.112.9',
              loggedAt: '2026-06-18T16:22:00'
            },
            {
              id: 'h7',
              success: true,
              deviceName: 'MacBook Pro 14',
              browser: 'Chrome',
              city: 'Москва',
              country: 'Россия',
              ip: '185.12.45.78',
              loggedAt: '2026-05-12T10:08:00'
            },
            {
              id: 'h8',
              success: false,
              deviceName: 'Unknown Device',
              browser: 'Opera',
              city: 'Киев',
              country: 'Украина',
              ip: '176.37.54.201',
              loggedAt: '2026-04-03T19:41:00'
            },
            {
              id: 'h9',
              success: true,
              deviceName: 'iPad Pro',
              browser: 'Safari',
              city: 'Екатеринбург',
              country: 'Россия',
              ip: '5.189.132.44',
              loggedAt: '2026-02-21T08:55:00'
            },
            {
              id: 'h10',
              success: true,
              deviceName: 'Windows Desktop',
              browser: 'Chrome',
              city: 'Москва',
              country: 'Россия',
              ip: '185.12.45.78',
              loggedAt: '2025-12-09T13:27:00'
            },
            {
              id: 'h11',
              success: false,
              deviceName: 'Android Phone',
              browser: 'Chrome',
              city: 'Ташкент',
              country: 'Узбекистан',
              ip: '213.230.96.15',
              loggedAt: '2025-10-14T23:11:00'
            },
            {
              id: 'h12',
              success: true,
              deviceName: 'MacBook Pro 14',
              browser: 'Safari',
              city: 'Москва',
              country: 'Россия',
              ip: '185.12.45.78',
              loggedAt: '2025-08-02T17:36:00'
            }
          ]
        },
        documents: {
          acceptedAtById: {
            offer: '2026-04-17',
            license: '2026-04-17',
            privacy: '2026-04-17',
            regulations: '2026-04-17'
          }
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
