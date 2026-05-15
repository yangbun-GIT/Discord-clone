import { defineStore } from 'pinia'
import { computed, shallowRef, ref } from 'vue'

import { apiGet, apiPost } from '../services/api'
import type { Channel, Guild, Invite, Message } from '../types'

export const useGuildStore = defineStore('guilds', () => {
  const guilds = shallowRef<Guild[]>([])
  const activeGuildId = ref<number | null>(null)
  const activeChannelId = ref<number | null>(null)
  const voiceConnected = ref(false)

  const activeGuild = computed(() => guilds.value.find((guild) => guild.id === activeGuildId.value) ?? null)
  const activeChannel = computed(
    () => activeGuild.value?.channels.find((channel) => channel.id === activeChannelId.value) ?? null,
  )
  const activeMessages = computed(() => {
    if (!activeChannel.value) return []
    return activeGuild.value?.messages.filter((message) => message.channel_id === activeChannel.value?.id) ?? []
  })
  const voiceChannel = computed(() => activeGuild.value?.channels.find((channel) => channel.type === 1) ?? null)

  async function loadGuilds(token: string | null) {
    guilds.value = await apiGet<Guild[]>('/api/guilds/me', token)
    activeGuildId.value = guilds.value[0]?.id ?? null
    activeChannelId.value = guilds.value[0]?.channels[0]?.id ?? null
  }

  async function createGuild(token: string | null, name: string) {
    const trimmedName = name.trim()
    if (!trimmedName) return
    const guild = await apiPost<Guild, { name: string }>('/api/guilds', { name: trimmedName }, token)
    guilds.value = [...guilds.value, guild]
    activeGuildId.value = guild.id
    activeChannelId.value = guild.channels[0]?.id ?? null
  }

  async function createInvite(token: string | null) {
    if (!activeGuild.value) return null
    return apiPost<Invite, Record<string, never>>(`/api/guilds/${activeGuild.value.id}/invites`, {}, token)
  }

  async function joinInvite(token: string | null, code: string) {
    const trimmedCode = code.trim()
    if (!trimmedCode) return
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
  }

  function resetGuilds() {
    guilds.value = []
    activeGuildId.value = null
    activeChannelId.value = null
    voiceConnected.value = false
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
  }

  async function sendMessage(token: string | null, content: string) {
    if (!activeChannel.value || activeChannel.value.type !== 0) return
    const message = await apiPost<Message, { channel_id: number; content: string }>(
      `/api/channels/${activeChannel.value.id}/messages`,
      { channel_id: activeChannel.value.id, content },
      token,
    )
    guilds.value = guilds.value.map((guild) => {
      if (!guild.channels.some((channel) => channel.id === message.channel_id)) return guild
      return { ...guild, messages: [...guild.messages, message] }
    })
  }

  return {
    guilds,
    activeGuildId,
    activeChannelId,
    activeGuild,
    activeChannel,
    activeMessages,
    voiceChannel,
    voiceConnected,
    loadGuilds,
    createGuild,
    createInvite,
    joinInvite,
    resetGuilds,
    selectGuild,
    selectChannel,
    toggleVoice,
    createChannel,
    sendMessage,
  }
})
