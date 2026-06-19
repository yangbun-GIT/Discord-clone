import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import type { DirectMessage, DmMessage, Friend } from '../types'
import {
  acceptRelationshipRequest,
  blockRelationshipUser,
  cancelRelationshipRequest,
  createDmChannel,
  createDmChannelMessage,
  loadDirectMessages,
  loadDmRelationships,
  loadDmWorkspace,
  rejectRelationshipRequest,
  removeRelationshipFriend,
  sendRelationshipRequest,
  unblockRelationshipUser,
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
  const activeDmId = ref<number | null>(null)

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

  function upsertRelationship(relationship: Friend) {
    const [cleanedRelationship] = cleanVisibleRelationships([relationship])
    if (!cleanedRelationship) return
    const exists = relationships.value.some((item) => item.id === cleanedRelationship.id)
    relationships.value = exists
      ? relationships.value.map((item) => (item.id === cleanedRelationship.id ? cleanedRelationship : item))
      : [...relationships.value, cleanedRelationship]
  }

  function removeRelationship(relationship: { id: number }) {
    relationships.value = relationships.value.filter((item) => item.id !== relationship.id)
  }

  function setActiveDm(dmId: number | null) {
    activeDmId.value = dmId
    if (dmId === null) return
    dms.value = dms.value.map((dm) => (
      dm.id === dmId ? { ...dm, unread_count: 0 } : dm
    ))
  }

  function appendMessage(
    dmId: number,
    message: DmMessage,
    options: { markUnread?: boolean } = {},
  ) {
    if (!isVisibleDmMessage(message)) return
    dms.value = dms.value.map((dm) => {
      if (dm.id !== dmId) return dm
      if (dm.messages.some((existingMessage) => existingMessage.id === message.id)) return dm
      const markUnread = options.markUnread ?? activeDmId.value !== dmId
      return {
        ...dm,
        unread_count: markUnread ? Math.min(dm.unread_count + 1, 999) : 0,
        messages: [...dm.messages, message],
      }
    })
  }

  function handleGatewayDispatch(event: string, data: Record<string, unknown>) {
    handleDmGatewayDispatch(event, data, {
      upsertDm,
      appendMessage,
      upsertRelationship,
      removeRelationship,
    })
  }

  async function sendFriendRequest(token: string | null, username: string) {
    const trimmedUsername = username.trim()
    if (!trimmedUsername) return null
    isMutating.value = true
    error.value = null
    try {
      const relationship = await sendRelationshipRequest(token, trimmedUsername)
      upsertRelationship(relationship)
      return relationship
    } catch (cause) {
      setError(cause, 'Failed to send friend request')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function acceptRequest(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await acceptRelationshipRequest(token, userId)
      upsertRelationship(relationship)
      return relationship
    } catch (cause) {
      setError(cause, 'Failed to accept friend request')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function rejectRequest(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await rejectRelationshipRequest(token, userId)
      removeRelationship(relationship)
    } catch (cause) {
      setError(cause, 'Failed to reject friend request')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function cancelRequest(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await cancelRelationshipRequest(token, userId)
      removeRelationship(relationship)
    } catch (cause) {
      setError(cause, 'Failed to cancel friend request')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function removeFriend(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await removeRelationshipFriend(token, userId)
      removeRelationship(relationship)
    } catch (cause) {
      setError(cause, 'Failed to remove friend')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function blockUser(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await blockRelationshipUser(token, userId)
      upsertRelationship(relationship)
      return relationship
    } catch (cause) {
      setError(cause, 'Failed to block user')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function unblockUser(token: string | null, userId: number) {
    isMutating.value = true
    error.value = null
    try {
      const relationship = await unblockRelationshipUser(token, userId)
      removeRelationship(relationship)
    } catch (cause) {
      setError(cause, 'Failed to unblock user')
      throw cause
    } finally {
      isMutating.value = false
    }
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
      appendMessage(dmId, message, { markUnread: false })
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
    activeDmId.value = null
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
    setActiveDm,
    createDm,
    sendDmMessage,
    sendFriendRequest,
    acceptRequest,
    rejectRequest,
    cancelRequest,
    removeFriend,
    blockUser,
    unblockUser,
    handleGatewayDispatch,
    resetDms,
  }
})
