import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import {
  createDirectMessage,
  createDirectMessageMessage,
  fetchDirectMessages,
  fetchRelationships,
} from '../services/api'
import type { DirectMessage, DmMessage, Friend } from '../types'
import { isVisualTestMessage, isVisualTestName } from '../utils/visualNoise'

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
      relationships.value = cleanRelationships(await fetchRelationships(token))
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
      dms.value = cleanDms(await fetchDirectMessages(token))
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
      relationships.value = cleanRelationships(nextRelationships)
      dms.value = cleanDms(nextDms)
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
    const cleanedDm = cleanDmForVisualQa(dm)
    if (!cleanedDm) return
    const exists = dms.value.some((item) => item.id === cleanedDm.id)
    dms.value = exists
      ? dms.value.map((item) => (item.id === cleanedDm.id ? cleanedDm : item))
      : [cleanedDm, ...dms.value]
  }

  function appendMessage(dmId: number, message: DmMessage) {
    if (isVisualTestMessage(message.content) || isVisualTestName(message.author_name)) return
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

  function cleanRelationships(nextRelationships: Friend[]) {
    return nextRelationships.filter(
      (friend) =>
        !isVisualTestName(friend.username)
        && !isVisualTestName(friend.handle)
        && !isVisualTestMessage(friend.activity),
    )
  }

  function cleanDmForVisualQa(dm: DirectMessage) {
    if (isVisualTestName(dm.display_name) || isVisualTestMessage(dm.activity)) return null
    return {
      ...dm,
      participants: dm.participants.filter(
        (participant) =>
          !isVisualTestName(participant.username)
          && !isVisualTestName(participant.handle)
          && !isVisualTestMessage(participant.activity),
      ),
      messages: dm.messages.filter(
        (message) => !isVisualTestName(message.author_name) && !isVisualTestMessage(message.content),
      ),
    }
  }

  function cleanDms(nextDms: DirectMessage[]) {
    return nextDms.flatMap((dm) => {
      const clean = cleanDmForVisualQa(dm)
      return clean ? [clean] : []
    })
  }

  function handleGatewayDispatch(event: string, data: Record<string, unknown>) {
    if (event === 'DM_CREATE') {
      const dm = data as DirectMessage
      if (
        typeof dm.id !== 'number'
        || !Array.isArray(dm.recipient_ids)
        || !Array.isArray(dm.participants)
        || typeof dm.display_name !== 'string'
        || !Array.isArray(dm.messages)
      ) {
        return
      }
      upsertDm(dm)
      return
    }

    if (event === 'DM_MESSAGE_CREATE') {
      const message = data as DmMessage
      if (
        typeof message.id !== 'number'
        || typeof message.dm_id !== 'number'
        || typeof message.author_id !== 'number'
        || typeof message.author_name !== 'string'
        || typeof message.content !== 'string'
      ) {
        return
      }
      appendMessage(message.dm_id, message)
    }
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
    handleGatewayDispatch,
    resetDms,
  }
})
