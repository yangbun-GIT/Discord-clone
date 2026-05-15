import { defineStore } from 'pinia'
import { ref } from 'vue'

import { apiGet, apiPost } from '../services/api'
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

export const useSessionStore = defineStore('session', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  function setSession(session: AuthSession) {
    token.value = session.access_token
    user.value = session.user
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
  }

  function clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem(SESSION_STORAGE_KEY)
  }

  async function restoreSession() {
    if (token.value) return
    const rawSession = localStorage.getItem(SESSION_STORAGE_KEY)
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
      username: 'yangbun',
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

  function logout() {
    clearSession()
  }

  return { token, user, restoreSession, ensureDevSession, login, register, logout }
})
