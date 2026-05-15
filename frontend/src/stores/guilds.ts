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
      const existing = guilds.value.some((item) => item.id === guild.id)
      guilds.value = existing
        ? guilds.value.map((item) => (item.id === guild.id ? guild : item))
        : [...guilds.value, guild]
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
      guilds.value = guilds.value.map((guild) => {
        if (guild.id !== channel.guild_id) return guild
        return { ...guild, channels: [...guild.channels, channel] }
      })
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
      guilds.value = guilds.value.map((guild) => {
        if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
        return { ...guild, messages: [...guild.messages, message] }
      })
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
    sendMessage,
  }
})
