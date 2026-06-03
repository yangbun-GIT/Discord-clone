import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import {
  createDirectMessage,
  createDirectMessageMessage,
  fetchDirectMessages,
  fetchRelationships,
} from '../services/api'
import type { DirectMessage, DmMessage, Friend } from '../types'

export const useDmStore = defineStore('dms', () => {
  const relationships = shallowRef<Friend[]>([])
  const dms = shallowRef<DirectMessage[]>([])
  const isLoading = ref(false)
  const isMutating = ref(false)
  const error = ref<string | null>(null)

  const unreadCount = computed(() =>
    dms.value.reduce((total, dm) => total + dm.unread_count, 0),
  )

  function setError(cause: unknown, fallback: string) {
    error.value = cause instanceof Error ? cause.message : fallback
  }

  async function loadRelationships(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      relationships.value = await fetchRelationships(token)
    } catch (cause) {
      setError(cause, 'Failed to load relationships')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  async function loadDms(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      dms.value = await fetchDirectMessages(token)
    } catch (cause) {
      setError(cause, 'Failed to load direct messages')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  async function loadPrivateWorkspace(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      const [nextRelationships, nextDms] = await Promise.all([
        fetchRelationships(token),
        fetchDirectMessages(token),
      ])
      relationships.value = nextRelationships
      dms.value = nextDms
    } catch (cause) {
      setError(cause, 'Failed to load direct messages')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  function getDm(dmId: number | null) {
    if (dmId === null) return null
    return dms.value.find((dm) => dm.id === dmId) ?? null
  }

  function upsertDm(dm: DirectMessage) {
    const exists = dms.value.some((item) => item.id === dm.id)
    dms.value = exists
      ? dms.value.map((item) => (item.id === dm.id ? dm : item))
      : [dm, ...dms.value]
  }

  function appendMessage(dmId: number, message: DmMessage) {
    dms.value = dms.value.map((dm) => {
      if (dm.id !== dmId) return dm
      if (dm.messages.some((existingMessage) => existingMessage.id === message.id)) return dm
      return {
        ...dm,
        unread_count: 0,
        messages: [...dm.messages, message],
      }
    })
  }

  async function createDm(token: string | null, recipientIds: number[]) {
    const uniqueRecipientIds = [...new Set(recipientIds)].filter((recipientId) => recipientId > 0)
    if (!uniqueRecipientIds.length) return null
    isMutating.value = true
    error.value = null
    try {
      const dm = await createDirectMessage({ recipient_ids: uniqueRecipientIds }, token)
      upsertDm(dm)
      return dm
    } catch (cause) {
      setError(cause, 'Failed to create direct message')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function sendDmMessage(token: string | null, dmId: number, content: string) {
    const trimmedContent = content.trim()
    if (!trimmedContent) return
    isMutating.value = true
    error.value = null
    try {
      const message = await createDirectMessageMessage(
        dmId,
        { dm_id: dmId, content: trimmedContent },
        token,
      )
      appendMessage(dmId, message)
    } catch (cause) {
      setError(cause, 'Failed to send direct message')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  function resetDms() {
    relationships.value = []
    dms.value = []
    isLoading.value = false
    isMutating.value = false
    error.value = null
  }

  return {
    relationships,
    dms,
    unreadCount,
    isLoading,
    isMutating,
    error,
    loadRelationships,
    loadDms,
    loadPrivateWorkspace,
    getDm,
    createDm,
    sendDmMessage,
    resetDms,
  }
})
