import { defineStore } from 'pinia'
import { ref } from 'vue'

import { apiPost } from '../services/api'
import type { User } from '../types'

type DevSession = {
  access_token: string
  token_type: string
  user: User
}

export const useSessionStore = defineStore('session', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)

  async function ensureDevSession() {
    if (token.value) return
    const session = await apiPost<DevSession, { username: string }>('/api/dev/session', {
      username: 'yangbun',
    })
    token.value = session.access_token
    user.value = session.user
  }

  return { token, user, ensureDevSession }
})

