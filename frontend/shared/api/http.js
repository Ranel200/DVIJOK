// Тонкая обёртка над fetch: базовый URL, JSON, обработка ошибок, токен авторизации.
// Переключение на реальный бэкенд — сменой USE_MOCK/baseURL.

export const USE_MOCK = String(import.meta.env.VITE_USE_MOCK).toLowerCase() !== 'false'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export class ApiError extends Error {
  constructor(message, { status, data } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

let authToken = null
let refreshPromise = null

export function setAuthToken(token) {
  authToken = token
}

export async function refreshAuthToken() {
  if (!refreshPromise) {
    const url = new URL(`${baseURL}/auth/refresh`, window.location.origin)

    refreshPromise = (async () => {
      const response = await fetch(url, {
        method: 'POST',
        credentials: 'include'
      })
      const isJson = response.headers.get('content-type')?.includes('application/json')
      const data = isJson ? await response.json() : await response.text()

      if (!response.ok) {
        throw new ApiError(`Refresh failed: ${response.status}`, {
          status: response.status,
          data
        })
      }

      const token = data?.token ?? data?.access_token
      if (!token) {
        throw new ApiError('Backend did not return access token')
      }

      setAuthToken(token)
      return token
    })().finally(() => {
      refreshPromise = null
    })
  }

  return refreshPromise
}

async function request(method, path, { params, body, headers } = {}) {
  const url = new URL(`${baseURL}${path}`, window.location.origin)

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, value)
      }
    }
  }

  const options = {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...headers
    }
  }

  if (body !== undefined) {
    options.body = JSON.stringify(body)
  }

  let response = await fetch(url, options)

  const publicAuthPaths = ['/auth/login', '/auth/register', '/auth/refresh']
  if (response.status === 401 && !publicAuthPaths.includes(path)) {
    try {
      const token = await refreshAuthToken()
      options.headers.Authorization = `Bearer ${token}`
      response = await fetch(url, options)
    } catch {
      setAuthToken(null)
    }
  }

  const isJson = response.headers.get('content-type')?.includes('application/json')
  const data = isJson ? await response.json() : await response.text()

  if (!response.ok) {
    throw new ApiError(`Request failed: ${response.status}`, {
      status: response.status,
      data
    })
  }

  return data
}

export const http = {
  get: (path, options) => request('GET', path, options),
  post: (path, body, options) => request('POST', path, { ...options, body }),
  put: (path, body, options) => request('PUT', path, { ...options, body }),
  patch: (path, body, options) => request('PATCH', path, { ...options, body }),
  delete: (path, options) => request('DELETE', path, options)
}
