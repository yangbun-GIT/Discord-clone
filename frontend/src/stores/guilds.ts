import { defineStore } from 'pinia'
import { computed, shallowRef, ref } from 'vue'

import { apiGet, apiPost, fetchServerRailLayout, updateServerRailLayout } from '../services/api'
import { runDocumentViewTransition } from '../services/browserApi'
import type { Channel, Guild, Message, MessageDelete, PresenceUpdate, ServerRailLayout } from '../types'
import { deleteChannelMessage, editChannelMessage, sendChannelMessage } from './channelMessages'
import {
  assignGuildRole,
  createGuildChannel,
  createGuildInvite,
  createGuildRole,
  joinGuildInvite,
  removeGuildMember,
  removeGuildRole,
} from './guildAdmin'
import { handleGuildGatewayDispatch } from './guildGatewayHandlers'
import {
  cleanVisibleGuild,
  cleanVisibleGuilds,
  isVisibleChannel,
  isVisibleGuildMessage,
} from './guildVisibility'
import { createGuildVoicePresence } from './voicePresence'

const ADMINISTRATOR_PERMISSION = 1 << 3
const CREATE_INSTANT_INVITE_PERMISSION = 1 << 0
const MANAGE_MESSAGES_PERMISSION = 1 << 13

export const useGuildStore = defineStore('guilds', () => {
  const guilds = shallowRef<Guild[]>([])
  const activeGuildId = ref<number | null>(null)
  const activeChannelId = ref<number | null>(null)
  const serverRailLayout = ref<ServerRailLayout>({ items: [], folders: [] })
  const isLoading = ref(false)
  const isMutating = ref(false)
  const error = ref<string | null>(null)

  const activeGuild = computed(() => guilds.value.find((guild) => guild.id === activeGuildId.value) ?? null)
  const activeChannel = computed(
    () => activeGuild.value?.channels.find((channel) => channel.id === activeChannelId.value) ?? null,
  )
  const activeMessages = computed(() => {
    if (!activeChannel.value) return []
    return activeGuild.value?.messages.filter((message) => message.channel_id === activeChannel.value?.id) ?? []
  })
  const voicePresence = createGuildVoicePresence({ guilds, activeGuild, activeChannel })
  const {
    voiceConnected,
    connectedVoiceGuildId,
    connectedVoiceChannelId,
    voiceStates,
    lastVoiceSignal,
    voiceChannel,
    connectedVoiceGuild,
    connectedVoiceChannel,
    activeVoiceStates,
    connectedVoiceStates,
    resetVoicePresence,
    toggleVoice,
    setVoiceConnected,
    syncVoiceState,
    syncVoiceSnapshot,
    setLastVoiceSignal,
  } = voicePresence
  const canManageRoles = computed(() => Boolean((activeGuild.value?.permissions ?? 0) & ADMINISTRATOR_PERMISSION))
  const canManageMessages = computed(() => {
    const permissions = activeGuild.value?.permissions ?? 0
    return Boolean((permissions & ADMINISTRATOR_PERMISSION) || (permissions & MANAGE_MESSAGES_PERMISSION))
  })
  const canCreateInvite = computed(() => {
    const permissions = activeGuild.value?.permissions ?? 0
    return Boolean((permissions & ADMINISTRATOR_PERMISSION) || (permissions & CREATE_INSTANT_INVITE_PERMISSION))
  })

  function setError(cause: unknown, fallback: string) {
    error.value = cause instanceof Error ? cause.message : fallback
  }

  function replaceGuild(updatedGuild: Guild) {
    const cleanGuild = cleanVisibleGuild(updatedGuild)
    if (!cleanGuild) {
      guilds.value = guilds.value.filter((guild) => guild.id !== updatedGuild.id)
      return
    }
    guilds.value = guilds.value.map((guild) => (guild.id === cleanGuild.id ? cleanGuild : guild))
  }

  function appendOrReplaceGuild(updatedGuild: Guild) {
    const cleanGuild = cleanVisibleGuild(updatedGuild)
    if (!cleanGuild) return
    const existing = guilds.value.some((guild) => guild.id === cleanGuild.id)
    guilds.value = existing
      ? guilds.value.map((guild) => (guild.id === cleanGuild.id ? cleanGuild : guild))
      : [...guilds.value, cleanGuild]
  }

  async function loadGuilds(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      const previousGuildId = activeGuildId.value
      const previousChannelId = activeChannelId.value
      const loadedGuilds = await apiGet<Guild[]>('/api/guilds/me', token)
      guilds.value = cleanVisibleGuilds(loadedGuilds)
      serverRailLayout.value = await fetchServerRailLayout(token)
      const preservedGuild = guilds.value.find((guild) => guild.id === previousGuildId)
      const nextGuild = preservedGuild ?? guilds.value[0] ?? null
      activeGuildId.value = nextGuild?.id ?? null
      activeChannelId.value = nextGuild?.channels.some((channel) => channel.id === previousChannelId)
        ? previousChannelId
        : nextGuild?.channels[0]?.id ?? null
    } catch (cause) {
      setError(cause, 'Failed to load servers')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  async function saveServerRailLayout(token: string | null, layout: ServerRailLayout) {
    const previousLayout = serverRailLayout.value
    serverRailLayout.value = layout
    try {
      serverRailLayout.value = await updateServerRailLayout(layout, token)
    } catch (cause) {
      serverRailLayout.value = previousLayout
      setError(cause, 'Failed to save server rail layout')
      throw cause
    }
  }

  async function refreshActiveGuild(token: string | null) {
    if (!activeGuild.value) return
    isLoading.value = true
    error.value = null
    try {
      const guild = await apiGet<Guild>(`/api/guilds/${activeGuild.value.id}`, token)
      appendOrReplaceGuild(guild)
      const cleanGuild = cleanVisibleGuild(guild)
      if (!cleanGuild) {
        activeGuildId.value = guilds.value[0]?.id ?? null
        activeChannelId.value = activeGuild.value?.channels[0]?.id ?? null
        return
      }
      activeGuildId.value = cleanGuild.id
      if (!cleanGuild.channels.some((channel) => channel.id === activeChannelId.value)) {
        activeChannelId.value = cleanGuild.channels[0]?.id ?? null
      }
    } catch (cause) {
      setError(cause, 'Failed to refresh server')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  async function createGuild(token: string | null, name: string) {
    const trimmedName = name.trim()
    if (!trimmedName) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await apiPost<Guild, { name: string }>('/api/guilds', { name: trimmedName }, token)
      appendOrReplaceGuild(guild)
      const cleanGuild = cleanVisibleGuild(guild)
      activeGuildId.value = cleanGuild?.id ?? activeGuildId.value
      activeChannelId.value = cleanGuild?.channels[0]?.id ?? activeChannelId.value
    } catch (cause) {
      setError(cause, 'Failed to create server')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function createInvite(token: string | null) {
    if (!activeGuild.value) return null
    isMutating.value = true
    error.value = null
    try {
      return await createGuildInvite(token, activeGuild.value.id)
    } catch (cause) {
      setError(cause, 'Failed to create invite')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function joinInvite(token: string | null, code: string) {
    const trimmedCode = code.trim()
    if (!trimmedCode) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await joinGuildInvite(token, trimmedCode)
      appendOrReplaceGuild(guild)
      const cleanGuild = cleanVisibleGuild(guild)
      activeGuildId.value = cleanGuild?.id ?? activeGuildId.value
      activeChannelId.value = cleanGuild?.channels[0]?.id ?? activeChannelId.value
    } catch (cause) {
      setError(cause, 'Failed to join server')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  function resetGuilds() {
    guilds.value = []
    activeGuildId.value = null
    activeChannelId.value = null
    resetVoicePresence()
    serverRailLayout.value = { items: [], folders: [] }
    isLoading.value = false
    isMutating.value = false
    error.value = null
  }

  function selectGuild(guildId: number) {
    activeGuildId.value = guildId
    activeChannelId.value = activeGuild.value?.channels[0]?.id ?? null
  }

  function selectChannel(channelId: number) {
    runDocumentViewTransition(() => {
      activeChannelId.value = channelId
    })
  }

  async function createChannel(token: string | null, name: string, type: 0 | 1 = 0) {
    if (!activeGuild.value) return
    const trimmedName = name.trim()
    if (!trimmedName) return
    isMutating.value = true
    error.value = null
    try {
      const channel = await createGuildChannel(token, activeGuild.value.id, { name: trimmedName, type })
      if (!isVisibleChannel(channel)) return
      appendChannel(channel)
      selectChannel(channel.id)
    } catch (cause) {
      setError(cause, 'Failed to create channel')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function createRole(token: string | null, name: string, permissions = 0) {
    if (!activeGuild.value) return
    const trimmedName = name.trim()
    if (!trimmedName) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await createGuildRole(token, activeGuild.value.id, {
        name: trimmedName,
        permissions,
      })
      replaceGuild(guild)
    } catch (cause) {
      setError(cause, 'Failed to create role')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function assignRole(token: string | null, memberId: number, roleId: number) {
    if (!activeGuild.value) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await assignGuildRole(token, activeGuild.value.id, memberId, roleId)
      replaceGuild(guild)
    } catch (cause) {
      setError(cause, 'Failed to assign role')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function removeRole(token: string | null, memberId: number, roleId: number) {
    if (!activeGuild.value) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await removeGuildRole(token, activeGuild.value.id, memberId, roleId)
      replaceGuild(guild)
    } catch (cause) {
      setError(cause, 'Failed to remove role')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function removeMember(token: string | null, memberId: number) {
    if (!activeGuild.value) return
    isMutating.value = true
    error.value = null
    try {
      const guild = await removeGuildMember(token, activeGuild.value.id, memberId)
      replaceGuild(guild)
    } catch (cause) {
      setError(cause, 'Failed to remove member')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  function appendMessage(message: Message) {
    if (!isVisibleGuildMessage(message)) return
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      if (guild.messages.some((existingMessage) => existingMessage.id === message.id)) return guild
      return { ...guild, messages: [...guild.messages, message] }
    })
  }

  function updateMessage(message: Message) {
    if (!isVisibleGuildMessage(message)) return
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      return {
        ...guild,
        messages: guild.messages.map((existingMessage) =>
          existingMessage.id === message.id ? message : existingMessage,
        ),
      }
    })
  }

  function deleteStoredMessage(message: MessageDelete) {
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      return {
        ...guild,
        messages: guild.messages.filter((existingMessage) => existingMessage.id !== message.id),
      }
    })
  }

  function appendChannel(channel: Channel) {
    if (!isVisibleChannel(channel)) return
    guilds.value = guilds.value.map((guild) => {
      if (guild.id !== channel.guild_id) return guild
      if (guild.channels.some((existingChannel) => existingChannel.id === channel.id)) return guild
      return { ...guild, channels: [...guild.channels, channel] }
    })
  }

  function syncGuildUpdate(guild: Guild) {
    appendOrReplaceGuild(guild)
    if (activeGuildId.value !== guild.id) return
    if (!guild.channels.some((channel) => channel.id === activeChannelId.value)) {
      activeChannelId.value = guild.channels[0]?.id ?? null
    }
  }

  function updatePresence(presence: PresenceUpdate) {
    guilds.value = guilds.value.map((guild) => {
      if (!guild.members.some((member) => member.id === presence.user_id)) return guild
      return {
        ...guild,
        members: guild.members.map((member) => (
          member.id === presence.user_id
            ? {
                ...member,
                username: presence.username ?? member.username,
                presence_status: presence.status,
              }
            : member
        )),
      }
    })
  }

  function handleGatewayDispatch(event: string, data: Record<string, unknown>) {
    handleGuildGatewayDispatch(event, data, {
      appendMessage,
      updateMessage,
      deleteStoredMessage,
      appendChannel,
      syncVoiceState,
      syncVoiceSnapshot,
      syncGuildUpdate,
      setLastVoiceSignal,
      updatePresence,
    })
  }

  async function sendMessage(token: string | null, content: string) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    isMutating.value = true
    error.value = null
    try {
      const message = await sendChannelMessage(token, activeChannel.value.id, content)
      appendMessage(message)
    } catch (cause) {
      setError(cause, 'Failed to send message')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function editMessage(token: string | null, messageId: number, content: string) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    const trimmedContent = content.trim()
    if (!trimmedContent) return
    isMutating.value = true
    error.value = null
    try {
      const message = await editChannelMessage(token, activeChannel.value.id, messageId, trimmedContent)
      updateMessage(message)
    } catch (cause) {
      setError(cause, 'Failed to edit message')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  async function deleteMessage(token: string | null, messageId: number) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    isMutating.value = true
    error.value = null
    try {
      const message = await deleteChannelMessage(token, activeChannel.value.id, messageId)
      deleteStoredMessage(message)
    } catch (cause) {
      setError(cause, 'Failed to delete message')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  return {
    guilds,
    activeGuildId,
    activeChannelId,
    activeGuild,
    activeChannel,
    activeMessages,
    serverRailLayout,
    voiceChannel,
    connectedVoiceGuild,
    connectedVoiceChannel,
    activeVoiceStates,
    connectedVoiceStates,
    canManageRoles,
    canManageMessages,
    canCreateInvite,
    voiceConnected,
    connectedVoiceGuildId,
    connectedVoiceChannelId,
    voiceStates,
    lastVoiceSignal,
    isLoading,
    isMutating,
    error,
    loadGuilds,
    saveServerRailLayout,
    refreshActiveGuild,
    createGuild,
    createInvite,
    joinInvite,
    resetGuilds,
    selectGuild,
    selectChannel,
    toggleVoice,
    setVoiceConnected,
    createChannel,
    createRole,
    assignRole,
    removeRole,
    removeMember,
    handleGatewayDispatch,
    sendMessage,
    editMessage,
    deleteMessage,
  }
})
