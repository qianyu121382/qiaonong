function getCookie(name) {
  const item = document.cookie
    .split('; ')
    .find((part) => part.startsWith(`${name}=`))
  return item ? decodeURIComponent(item.split('=').slice(1).join('=')) : ''
}

function errorMessage(data, fallback) {
  if (typeof data === 'string') {
    const message = data.trim()
    return message.startsWith('<!DOCTYPE') || message.startsWith('<html') ? fallback : message
  }
  if (data?.detail) return data.detail
  if (data && typeof data === 'object') {
    return Object.entries(data)
      .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join('，') : value}`)
      .join('；')
  }
  return fallback
}

export async function api(path, options = {}) {
  const method = options.method || 'GET'
  const headers = new Headers(options.headers || {})
  let body = options.body

  if (body && !(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(body)
  }
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method.toUpperCase())) {
    headers.set('X-CSRFToken', getCookie('csrftoken'))
  }

  const response = await fetch(path, {
    ...options,
    method,
    headers,
    body,
    credentials: 'same-origin',
  })
  if (response.status === 204) return null

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()
  if (!response.ok) {
    const error = new Error(errorMessage(data, `请求失败（${response.status}）`))
    error.status = response.status
    error.data = data
    throw error
  }
  return data
}

export function appendValue(form, key, value) {
  if (value !== undefined && value !== null && value !== '') form.append(key, value)
}
