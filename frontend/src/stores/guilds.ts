import { defineStore } from 'pinia'
import { computed, shallowRef, ref } from 'vue'

import { apiDelete, apiGet, apiPost } from '../services/api'
import type { Channel, Guild, Invite, Message } from '../types'

const ADMINISTRATOR_PERMISSION = 1 << 3

export const useGuildStore = defineStore('guilds', () => {
  const guilds = shallowRef<Guild[]>([])
  const activeGuildId = ref<number | null>(null)
  const activeChannelId = ref<number | null>(null)
  const voiceConnected = ref(false)
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
  const voiceChannel = computed(() => activeGuild.value?.channels.find((channel) => channel.type === 1) ?? null)
  const canManageRoles = computed(() => Boolean((activeGuild.value?.permissions ?? 0) & ADMINISTRATOR_PERMISSION))

  function setError(cause: unknown, fallback: string) {
    error.value = cause instanceof Error ? cause.message : fallback
  }

  function replaceGuild(updatedGuild: Guild) {
    guilds.value = guilds.value.map((guild) => (guild.id === updatedGuild.id ? updatedGuild : guild))
  }

  function appendOrReplaceGuild(updatedGuild: Guild) {
    const existing = guilds.value.some((guild) => guild.id === updatedGuild.id)
    guilds.value = existing
      ? guilds.value.map((guild) => (guild.id === updatedGuild.id ? updatedGuild : guild))
      : [...guilds.value, updatedGuild]
  }

  async function loadGuilds(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      guilds.value = await apiGet<Guild[]>('/api/guilds/me', token)
      activeGuildId.value = guilds.value[0]?.id ?? null
      activeChannelId.value = guilds.value[0]?.channels[0]?.id ?? null
    } catch (cause) {
      setError(cause, 'Failed to load servers')
      throw cause
    } finally {
      isLoading.value = false
    }
  }

  async function refreshActiveGuild(token: string | null) {
    if (!activeGuild.value) return
    isLoading.value = true
    error.value = null
    try {
      const guild = await apiGet<Guild>(`/api/guilds/${activeGuild.value.id}`, token)
      appendOrReplaceGuild(guild)
      activeGuildId.value = guild.id
      if (!guild.channels.some((channel) => channel.id === activeChannelId.value)) {
        activeChannelId.value = guild.channels[0]?.id ?? null
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
      guilds.value = [...guilds.value, guild]
      activeGuildId.value = guild.id
      activeChannelId.value = guild.channels[0]?.id ?? null
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
      return await apiPost<Invite, Record<string, never>>(`/api/guilds/${activeGuild.value.id}/invites`, {}, token)
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
      const guild = await apiPost<Guild, Record<string, never>>(
        `/api/guilds/invites/${encodeURIComponent(trimmedCode)}/join`,
        {},
        token,
      )
      appendOrReplaceGuild(guild)
      activeGuildId.value = guild.id
      activeChannelId.value = guild.channels[0]?.id ?? null
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
    voiceConnected.value = false
    isLoading.value = false
    isMutating.value = false
    error.value = null
  }

  function selectGuild(guildId: number) {
    activeGuildId.value = guildId
    activeChannelId.value = activeGuild.value?.channels[0]?.id ?? null
  }

  function selectChannel(channelId: number) {
    const startViewTransition = document.startViewTransition
    if (startViewTransition) {
      startViewTransition.call(document, () => {
        activeChannelId.value = channelId
      })
      return
    }
    activeChannelId.value = channelId
  }

  function toggleVoice() {
    voiceConnected.value = !voiceConnected.value
  }

  async function createChannel(token: string | null, name: string, type: 0 | 1 = 0) {
    if (!activeGuild.value) return
    const trimmedName = name.trim()
    if (!trimmedName) return
    isMutating.value = true
    error.value = null
    try {
      const channel = await apiPost<Channel, { name: string; type: 0 | 1 }>(
        `/api/guilds/${activeGuild.value.id}/channels`,
        { name: trimmedName, type },
        token,
      )
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
      const guild = await apiPost<Guild, { name: string; permissions: number }>(
        `/api/guilds/${activeGuild.value.id}/roles`,
        { name: trimmedName, permissions },
        token,
      )
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
      const guild = await apiPost<Guild, { role_id: number }>(
        `/api/guilds/${activeGuild.value.id}/members/${memberId}/roles`,
        { role_id: roleId },
        token,
      )
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
      const guild = await apiDelete<Guild>(
        `/api/guilds/${activeGuild.value.id}/members/${memberId}/roles/${roleId}`,
        token,
      )
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
      const guild = await apiDelete<Guild>(
        `/api/guilds/${activeGuild.value.id}/members/${memberId}`,
        token,
      )
      replaceGuild(guild)
    } catch (cause) {
      setError(cause, 'Failed to remove member')
      throw cause
    } finally {
      isMutating.value = false
    }
  }

  function appendMessage(message: Message) {
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      if (guild.messages.some((existingMessage) => existingMessage.id === message.id)) return guild
      return { ...guild, messages: [...guild.messages, message] }
    })
  }

  function appendChannel(channel: Channel) {
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

  function handleGatewayDispatch(event: string, data: Record<string, unknown>) {
    if (event === 'MESSAGE_CREATE') {
      const message = data as Message
      if (
        typeof message.id !== 'number'
        || typeof message.channel_id !== 'number'
        || typeof message.author_id !== 'number'
        || typeof message.author_name !== 'string'
        || typeof message.content !== 'string'
      ) {
        return
      }
      appendMessage(message)
      return
    }
    if (event === 'CHANNEL_CREATE') {
      const channel = data as Channel
      if (
        typeof channel.id !== 'number'
        || typeof channel.guild_id !== 'number'
        || typeof channel.name !== 'string'
        || typeof channel.type !== 'number'
        || typeof channel.position !== 'number'
      ) {
        return
      }
      appendChannel(channel)
      return
    }
    if (event === 'GUILD_UPDATE') {
      const guild = data as Guild
      if (
        typeof guild.id !== 'number'
        || typeof guild.name !== 'string'
        || !Array.isArray(guild.channels)
        || !Array.isArray(guild.members)
        || !Array.isArray(guild.messages)
      ) {
        return
      }
      syncGuildUpdate(guild)
    }
  }

  async function sendMessage(token: string | null, content: string) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    isMutating.value = true
    error.value = null
    try {
      const message = await apiPost<Message, { channel_id: number; content: string }>(
        `/api/channels/${activeChannel.value.id}/messages`,
        { channel_id: activeChannel.value.id, content },
        token,
      )
      appendMessage(message)
    } catch (cause) {
      setError(cause, 'Failed to send message')
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
    voiceChannel,
    canManageRoles,
    voiceConnected,
    isLoading,
    isMutating,
    error,
    loadGuilds,
    refreshActiveGuild,
    createGuild,
    createInvite,
    joinInvite,
    resetGuilds,
    selectGuild,
    selectChannel,
    toggleVoice,
    createChannel,
    createRole,
    assignRole,
    removeRole,
    removeMember,
    handleGatewayDispatch,
    sendMessage,
  }
})
