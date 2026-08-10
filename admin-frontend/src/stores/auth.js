import { reactive } from 'vue'

import { api } from '../api'


export const authState = reactive({ ready: false, authenticated: false, user: null })

function applySession(data) {
  authState.authenticated = Boolean(data.authenticated)
  authState.user = data.user
  authState.ready = true
}

export async function restoreSession() {
  try {
    applySession(await api('/api/admin/auth/me/'))
  } catch {
    applySession({ authenticated: false, user: null })
  }
}

export async function login(username, password) {
  if (!authState.ready) await restoreSession()
  const data = await api('/api/admin/auth/login/', {
    method: 'POST',
    body: { username, password },
  })
  applySession(data)
}

export async function logout() {
  await api('/api/admin/auth/logout/', { method: 'POST' })
  applySession({ authenticated: false, user: null })
}
