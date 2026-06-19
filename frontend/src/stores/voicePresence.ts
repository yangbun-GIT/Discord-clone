import { computed, ref, shallowRef, type ComputedRef, type ShallowRef } from 'vue'

import type { Channel, Guild, VoiceSignal, VoiceState, VoiceStateSnapshot } from '../types'

interface GuildVoicePresenceOptions {
  guilds: ShallowRef<Guild[]>
  activeGuild: ComputedRef<Guild | null>
  activeChannel: ComputedRef<Channel | null>
}

export function createGuildVoicePresence(options: GuildVoicePresenceOptions) {
  const voiceConnected = ref(false)
  const connectedVoiceGuildId = ref<number | null>(null)
  const connectedVoiceChannelId = ref<number | null>(null)
  const voiceStates = shallowRef<VoiceState[]>([])
  const lastVoiceSignal = ref<VoiceSignal | null>(null)

  const voiceChannel = computed(() => {
    if (options.activeChannel.value?.type === 1) return options.activeChannel.value
    return options.activeGuild.value?.channels.find((channel) => channel.type === 1) ?? null
  })
  const connectedVoiceGuild = computed(
    () => options.guilds.value.find((guild) => guild.id === connectedVoiceGuildId.value) ?? null,
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

  function resetVoicePresence() {
    voiceConnected.value = false
    connectedVoiceGuildId.value = null
    connectedVoiceChannelId.value = null
    voiceStates.value = []
    lastVoiceSignal.value = null
  }

  function toggleVoice() {
    voiceConnected.value = !voiceConnected.value
  }

  function setVoiceConnected(connected: boolean, channel: Channel | null = null) {
    voiceConnected.value = connected
    connectedVoiceGuildId.value = connected ? channel?.guild_id ?? connectedVoiceGuildId.value : null
    connectedVoiceChannelId.value = connected ? channel?.id ?? connectedVoiceChannelId.value : null
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

  function syncVoiceSnapshot(snapshot: VoiceStateSnapshot) {
    const guildIds = new Set(snapshot.guild_ids)
    const nextStates = snapshot.states
    voiceStates.value = [
      ...voiceStates.value.filter((state) => {
        if (!guildIds.has(state.guild_id)) return true
        if (snapshot.channel_id === null) return false
        return state.channel_id !== snapshot.channel_id
      }),
      ...nextStates,
    ]
  }

  function setLastVoiceSignal(signal: VoiceSignal) {
    lastVoiceSignal.value = signal
  }

  return {
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
  }
}
