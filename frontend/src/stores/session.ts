import { defineStore } from 'pinia'
import { ref } from 'vue'

import { apiGet, apiPost } from '../services/api'
import { browserStorage } from '../services/browserApi'
import type { User } from '../types'

type AuthSession = {
  access_token: string
  token_type: string
  user: User
}

type AuthCredentials = {
  username: string
  password: string
}

const SESSION_STORAGE_KEY = 'discord-clone-session'
const DEVELOPMENT_ADMIN_USER_ID = 42

export const useSessionStore = defineStore('session', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  function setSession(session: AuthSession) {
    token.value = session.access_token
    user.value = session.user
    browserStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
  }

  function clearSession() {
    token.value = null
    user.value = null
    browserStorage.removeItem(SESSION_STORAGE_KEY)
  }

  async function restoreSession() {
    if (token.value) return
    const rawSession = browserStorage.getItem(SESSION_STORAGE_KEY)
    if (!rawSession) return

    try {
      const savedSession = JSON.parse(rawSession) as AuthSession
      const currentUser = await apiGet<User>('/api/auth/me', savedSession.access_token)
      setSession({ ...savedSession, user: currentUser })
    } catch {
      clearSession()
    }
  }

  async function ensureDevSession() {
    if (token.value) return
    const session = await apiPost<AuthSession, { username: string }>('/api/dev/session', {
      username: 'admin',
    })
    setSession(session)
  }

  async function login(credentials: AuthCredentials) {
    const session = await apiPost<AuthSession, AuthCredentials>('/api/auth/login', credentials)
    setSession(session)
  }

  async function register(credentials: AuthCredentials) {
    const session = await apiPost<AuthSession, AuthCredentials>('/api/auth/register', credentials)
    setSession(session)
  }

  async function resetDevelopmentSessionIfNeeded() {
    const currentToken = token.value
    if (!currentToken || user.value?.id !== DEVELOPMENT_ADMIN_USER_ID) return

    try {
      await apiPost<{ reset: boolean }, Record<string, never>>(
        '/api/dev/session/reset',
        {},
        currentToken,
      )
    } catch {
      // Logout must still succeed even if the local reset endpoint is unavailable.
    }
  }

  async function logout() {
    await resetDevelopmentSessionIfNeeded()
    clearSession()
  }

  return { token, user, restoreSession, ensureDevSession, login, register, logout }
})
