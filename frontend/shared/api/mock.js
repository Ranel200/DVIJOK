// Хелперы для работы с моками, пока нет реального бэкенда.

import { ApiError } from './http.js'

const DEFAULT_DELAY = 300

export function delay(ms = DEFAULT_DELAY) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Имитация успешного ответа сервера с задержкой.
export async function mockOk(data, ms = DEFAULT_DELAY) {
  await delay(ms)
  return data
}

// Имитация ошибки сервера с задержкой.
export async function mockReject(status, data, ms = DEFAULT_DELAY) {
  await delay(ms)
  throw new ApiError(`Mock error: ${status}`, { status, data })
}
