import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import type { DirectMessage, DmMessage, Friend } from '../types'
import {
  createDmChannel,
  createDmChannelMessage,
  loadDirectMessages,
  loadDmRelationships,
  loadDmWorkspace,
} from './dmApi'
import { handleDmGatewayDispatch } from './dmGatewayHandlers'
import {
  cleanVisibleDirectMessage,
  cleanVisibleDirectMessages,
  cleanVisibleRelationships,
  isVisibleDmMessage,
} from './dmVisibility'

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
      relationships.value = cleanVisibleRelationships(await loadDmRelationships(token))
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
      dms.value = cleanVisibleDirectMessages(await loadDirectMessages(token))
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
      const workspace = await loadDmWorkspace(token)
      relationships.value = cleanVisibleRelationships(workspace.relationships)
      dms.value = cleanVisibleDirectMessages(workspace.directMessages)
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
    const cleanedDm = cleanVisibleDirectMessage(dm)
    if (!cleanedDm) return
    const exists = dms.value.some((item) => item.id === cleanedDm.id)
    dms.value = exists
      ? dms.value.map((item) => (item.id === cleanedDm.id ? cleanedDm : item))
      : [cleanedDm, ...dms.value]
  }

  function appendMessage(dmId: number, message: DmMessage) {
    if (!isVisibleDmMessage(message)) return
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

  function handleGatewayDispatch(event: string, data: Record<string, unknown>) {
    handleDmGatewayDispatch(event, data, { upsertDm, appendMessage })
  }

  async function createDm(token: string | null, recipientIds: number[]) {
    const dmPromise = createDmChannel(token, recipientIds)
    if (!dmPromise) return null
    isMutating.value = true
    error.value = null
    try {
      const dm = await dmPromise
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
    const messagePromise = createDmChannelMessage(token, dmId, content)
    if (!messagePromise) return
    isMutating.value = true
    error.value = null
    try {
      const message = await messagePromise
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
