import { defineStore } from 'pinia'
import { computed, shallowRef, ref } from 'vue'

import { apiDelete, apiGet, apiPatch, apiPost } from '../services/api'
import type { Channel, Guild, Invite, Message, MessageDelete, VoiceSignal, VoiceState } from '../types'
import { isVisualTestMessage, isVisualTestName } from '../utils/visualNoise'

const ADMINISTRATOR_PERMISSION = 1 << 3
const MANAGE_MESSAGES_PERMISSION = 1 << 13

export const useGuildStore = defineStore('guilds', () => {
  const guilds = shallowRef<Guild[]>([])
  const activeGuildId = ref<number | null>(null)
  const activeChannelId = ref<number | null>(null)
  const voiceConnected = ref(false)
  const connectedVoiceGuildId = ref<number | null>(null)
  const connectedVoiceChannelId = ref<number | null>(null)
  const voiceStates = shallowRef<VoiceState[]>([])
  const lastVoiceSignal = ref<VoiceSignal | null>(null)
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
  const voiceChannel = computed(() => {
    if (activeChannel.value?.type === 1) return activeChannel.value
    return activeGuild.value?.channels.find((channel) => channel.type === 1) ?? null
  })
  const connectedVoiceGuild = computed(
    () => guilds.value.find((guild) => guild.id === connectedVoiceGuildId.value) ?? null,
  )
  const connectedVoiceChannel = computed(() => {
    if (!connectedVoiceChannelId.value) return null
    return connectedVoiceGuild.value?.channels.find((channel) => channel.id === connectedVoiceChannelId.value) ?? null
  })
  const activeVoiceStates = computed(() => {
    if (!voiceChannel.value) return []
    return voiceStates.value.filter((state) => state.channel_id === voiceChannel.value?.id)
  })
  const connectedVoiceStates = computed(() => {
    if (!connectedVoiceChannelId.value) return []
    return voiceStates.value.filter((state) => state.channel_id === connectedVoiceChannelId.value)
  })
  const canManageRoles = computed(() => Boolean((activeGuild.value?.permissions ?? 0) & ADMINISTRATOR_PERMISSION))
  const canManageMessages = computed(() => {
    const permissions = activeGuild.value?.permissions ?? 0
    return Boolean((permissions & ADMINISTRATOR_PERMISSION) || (permissions & MANAGE_MESSAGES_PERMISSION))
  })

  function setError(cause: unknown, fallback: string) {
    error.value = cause instanceof Error ? cause.message : fallback
  }

  function replaceGuild(updatedGuild: Guild) {
    const cleanGuild = cleanGuildForVisualQa(updatedGuild)
    if (!cleanGuild) {
      guilds.value = guilds.value.filter((guild) => guild.id !== updatedGuild.id)
      return
    }
    guilds.value = guilds.value.map((guild) => (guild.id === cleanGuild.id ? cleanGuild : guild))
  }

  function appendOrReplaceGuild(updatedGuild: Guild) {
    const cleanGuild = cleanGuildForVisualQa(updatedGuild)
    if (!cleanGuild) return
    const existing = guilds.value.some((guild) => guild.id === cleanGuild.id)
    guilds.value = existing
      ? guilds.value.map((guild) => (guild.id === cleanGuild.id ? cleanGuild : guild))
      : [...guilds.value, cleanGuild]
  }

  function cleanGuildForVisualQa(guild: Guild) {
    if (isVisualTestName(guild.name)) return null
    const visibleChannels = guild.channels.filter((channel) => !isVisualTestName(channel.name))
    const visibleChannelIds = new Set(visibleChannels.map((channel) => channel.id))
    return {
      ...guild,
      channels: visibleChannels,
      messages: guild.messages.filter(
        (message) =>
          visibleChannelIds.has(message.channel_id)
          && !isVisualTestMessage(message.content)
          && !isVisualTestName(message.author_name),
      ),
    }
  }

  async function loadGuilds(token: string | null) {
    isLoading.value = true
    error.value = null
    try {
      const loadedGuilds = await apiGet<Guild[]>('/api/guilds/me', token)
      guilds.value = loadedGuilds.flatMap((guild) => {
        const cleanGuild = cleanGuildForVisualQa(guild)
        return cleanGuild ? [cleanGuild] : []
      })
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
      const cleanGuild = cleanGuildForVisualQa(guild)
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
      const cleanGuild = cleanGuildForVisualQa(guild)
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
      const cleanGuild = cleanGuildForVisualQa(guild)
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
    voiceConnected.value = false
    connectedVoiceGuildId.value = null
    connectedVoiceChannelId.value = null
    voiceStates.value = []
    lastVoiceSignal.value = null
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

  function setVoiceConnected(connected: boolean, channel: Channel | null = null) {
    voiceConnected.value = connected
    connectedVoiceGuildId.value = connected ? channel?.guild_id ?? connectedVoiceGuildId.value : null
    connectedVoiceChannelId.value = connected ? channel?.id ?? connectedVoiceChannelId.value : null
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
      if (isVisualTestName(channel.name)) return
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
    if (isVisualTestMessage(message.content) || isVisualTestName(message.author_name)) return
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      if (guild.messages.some((existingMessage) => existingMessage.id === message.id)) return guild
      return { ...guild, messages: [...guild.messages, message] }
    })
  }

  function updateMessage(message: Message) {
    if (isVisualTestMessage(message.content) || isVisualTestName(message.author_name)) return
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
    if (isVisualTestName(channel.name)) return
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

  function syncVoiceState(voiceState: VoiceState) {
    voiceStates.value = [
      ...voiceStates.value.filter(
        (state) =>
          !(state.guild_id === voiceState.guild_id && state.user_id === voiceState.user_id),
      ),
      ...(voiceState.channel_id === null ? [] : [voiceState]),
    ]
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
    if (event === 'MESSAGE_UPDATE') {
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
      updateMessage(message)
      return
    }
    if (event === 'MESSAGE_DELETE') {
      const message = data as MessageDelete
      if (typeof message.id !== 'number' || typeof message.channel_id !== 'number') {
        return
      }
      deleteStoredMessage(message)
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
    if (event === 'VOICE_STATE_UPDATE') {
      const voiceState = data as VoiceState
      if (
        typeof voiceState.guild_id !== 'number'
        || (voiceState.channel_id !== null && typeof voiceState.channel_id !== 'number')
        || typeof voiceState.user_id !== 'number'
        || typeof voiceState.self_mute !== 'boolean'
        || typeof voiceState.self_deaf !== 'boolean'
      ) {
        return
      }
      syncVoiceState(voiceState)
      return
    }
    if (event === 'VOICE_SIGNAL') {
      const signal = data as VoiceSignal
      if (
        typeof signal.channel_id !== 'number'
        || typeof signal.from_user_id !== 'number'
        || typeof signal.target_user_id !== 'number'
        || !['offer', 'answer', 'ice'].includes(signal.type)
      ) {
        return
      }
      lastVoiceSignal.value = signal
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

  async function editMessage(token: string | null, messageId: number, content: string) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    const trimmedContent = content.trim()
    if (!trimmedContent) return
    isMutating.value = true
    error.value = null
    try {
      const message = await apiPatch<Message, { content: string }>(
        `/api/channels/${activeChannel.value.id}/messages/${messageId}`,
        { content: trimmedContent },
        token,
      )
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
      const message = await apiDelete<MessageDelete>(
        `/api/channels/${activeChannel.value.id}/messages/${messageId}`,
        token,
      )
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
    voiceChannel,
    connectedVoiceGuild,
    connectedVoiceChannel,
    activeVoiceStates,
    connectedVoiceStates,
    canManageRoles,
    canManageMessages,
    voiceConnected,
    connectedVoiceGuildId,
    connectedVoiceChannelId,
    voiceStates,
    lastVoiceSignal,
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
