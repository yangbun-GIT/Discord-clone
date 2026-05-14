import { defineStore } from 'pinia'
import { computed, shallowRef, ref } from 'vue'

import { apiGet } from '../services/api'
import type { Guild } from '../types'

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

  async function loadGuilds() {
    guilds.value = await apiGet<Guild[]>('/api/guilds/me')
    activeGuildId.value = guilds.value[0]?.id ?? null
    activeChannelId.value = guilds.value[0]?.channels[0]?.id ?? null
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
    selectGuild,
    selectChannel,
    toggleVoice,
  }
})
