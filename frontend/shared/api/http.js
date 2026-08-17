// Тонкая обёртка над fetch: базовый URL, JSON, обработка ошибок, токен авторизации.
// Переключение на реальный бэкенд — сменой USE_MOCK/baseURL.

const runtimeEnv = import.meta.env

// Quasar CLI exposes dotenv values with the QCLI_ prefix. Keep the VITE_
// fallback so this shared module also works in plain Vite applications.
export const USE_MOCK =
  import.meta.env.DEV &&
  String(runtimeEnv.QCLI_USE_MOCK ?? runtimeEnv.VITE_USE_MOCK ?? 'false').toLowerCase() === 'true'

const baseURL = runtimeEnv.QCLI_API_BASE_URL ?? runtimeEnv.VITE_API_BASE_URL ?? '/api/v1'

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
let authFailureHandler = null
let refreshPath = '/auth/refresh'
let publicAuthPaths = new Set(['/auth/login', '/auth/register', '/auth/refresh'])

export function setAuthToken(token) {
  authToken = token
}

export function setAuthFailureHandler(handler) {
  authFailureHandler = typeof handler === 'function' ? handler : null
}

export function configureAuthFlow({ refresh, publicPaths } = {}) {
  if (refresh) refreshPath = refresh
  if (Array.isArray(publicPaths)) publicAuthPaths = new Set(publicPaths)
}

export async function refreshAuthToken() {
  if (!refreshPromise) {
    const url = new URL(`${baseURL}${refreshPath}`, window.location.origin)

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

  if (response.status === 401 && !publicAuthPaths.has(path)) {
    try {
      const token = await refreshAuthToken()
      options.headers.Authorization = `Bearer ${token}`
      response = await fetch(url, options)
    } catch {
      setAuthToken(null)
      authFailureHandler?.()
    }
  }

  const responseText = response.status === 204 ? '' : await response.text()
  const isJson = response.headers.get('content-type')?.includes('application/json')
  let data = responseText

  if (isJson && responseText) {
    try {
      data = JSON.parse(responseText)
    } catch {
      data = responseText
    }
  }

  if (!response.ok) {
    throw new ApiError(`Request failed: ${response.status}`, {
      status: response.status,
      data
    })
  }

  return data
}

async function requestRaw(method, path, { params, body, headers } = {}) {
  const url = new URL(`${baseURL}${path}`, window.location.origin)

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) url.searchParams.set(key, value)
    }
  }

  const options = {
    method,
    credentials: 'include',
    headers: {
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...headers
    }
  }
  if (body !== undefined) options.body = JSON.stringify(body)

  let response = await fetch(url, options)
  if (response.status === 401 && !publicAuthPaths.has(path)) {
    try {
      const token = await refreshAuthToken()
      options.headers.Authorization = `Bearer ${token}`
      response = await fetch(url, options)
    } catch {
      setAuthToken(null)
      authFailureHandler?.()
    }
  }
  if (!response.ok) {
    const isJson = response.headers.get('content-type')?.includes('application/json')
    const data = isJson ? await response.json() : await response.text()
    throw new ApiError(`Request failed: ${response.status}`, {
      status: response.status,
      data
    })
  }
  return response
}

async function requestForm(method, path, formData, { params, headers } = {}) {
  const url = new URL(`${baseURL}${path}`, window.location.origin)

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) url.searchParams.set(key, value)
    }
  }

  const options = {
    method,
    credentials: 'include',
    headers: {
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...headers
    },
    body: formData
  }

  let response = await fetch(url, options)
  if (response.status === 401 && !publicAuthPaths.has(path)) {
    try {
      const token = await refreshAuthToken()
      options.headers.Authorization = `Bearer ${token}`
      response = await fetch(url, options)
    } catch {
      setAuthToken(null)
      authFailureHandler?.()
    }
  }

  const responseText = response.status === 204 ? '' : await response.text()
  const isJson = response.headers.get('content-type')?.includes('application/json')
  let data = responseText
  if (isJson && responseText) {
    try {
      data = JSON.parse(responseText)
    } catch {
      data = responseText
    }
  }
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
  delete: (path, options) => request('DELETE', path, options),
  raw: (path, options) => requestRaw('GET', path, options),
  postForm: (path, formData, options) => requestForm('POST', path, formData, options)
}
