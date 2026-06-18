import { computed, ref, watch } from 'vue'

import { apiGet } from '../services/api'
import { browserStorage } from '../services/browserApi'
import type { TranslationKey } from '../i18n'
import type { Channel, Guild, User, VoiceConfig, VoiceIceServer, VoiceSignal, VoiceState } from '../types'
import type { useGateway } from './useGateway'
import type { useVoiceRtc } from './useVoiceRtc'
import type { useGuildStore } from '../stores/guilds'
import type { useSessionStore } from '../stores/session'

type GuildStore = ReturnType<typeof useGuildStore>
type SessionStore = ReturnType<typeof useSessionStore>
type VoiceRtc = ReturnType<typeof useVoiceRtc>
type Gateway = ReturnType<typeof useGateway>

interface VoiceSessionControllerOptions {
  guilds: GuildStore
  session: SessionStore
  voiceRtc: VoiceRtc
  activeGuild: () => Guild | null | undefined
  activeChannel: () => Channel | null | undefined
  updateVoiceState: Gateway['updateVoiceState']
  sendVoiceSignal: Gateway['sendVoiceSignal']
  setError: (message: string | null) => void
  t: (key: TranslationKey) => string
}

export function useVoiceSessionController(options: VoiceSessionControllerOptions) {
  const isDeafened = ref(false)
  const pendingVoiceSwitchChannelId = ref<number | null>(null)
  const skipVoiceSwitchConfirm = ref(browserStorage.getItem('discord_clone_skip_voice_switch_confirm') === 'true')
  const rememberVoiceSwitchChoice = ref(false)
  const voiceIceServers = ref<VoiceIceServer[]>([{ urls: 'stun:stun.l.google.com:19302' }])
  const voiceTurnConfigured = ref(false)

  const connectedVoiceChannelId = computed(() =>
    options.guilds.voiceConnected ? options.guilds.connectedVoiceChannelId : null,
  )
  const activeGuildConnectedVoiceChannelId = computed(() =>
    options.guilds.connectedVoiceGuildId === options.activeGuild()?.id ? connectedVoiceChannelId.value : null,
  )
  const voicePanelChannel = computed(() =>
    options.guilds.voiceConnected ? options.guilds.connectedVoiceChannel : options.guilds.voiceChannel,
  )
  const selectedVoiceChannel = computed(() => {
    const channel = options.activeChannel()
    return channel?.type === 1 ? channel : null
  })
  const selectedVoiceParticipants = computed(() =>
    selectedVoiceChannel.value ? voiceParticipantsForChannel(selectedVoiceChannel.value.id) : [],
  )
  const selectedVoicePeers = computed(() =>
    selectedVoiceParticipants.value.filter((state) => state.user_id !== options.session.user?.id),
  )
  const selectedVoiceConnected = computed(() =>
    selectedVoiceChannel.value?.id === connectedVoiceChannelId.value,
  )
  const voiceWorkspaceStatus = computed(() => {
    if (!selectedVoiceChannel.value) return options.t('voice.selectToPreview')
    if (selectedVoiceConnected.value) {
      if (options.voiceRtc.isScreenSharing.value) return options.t('voice.screenLive')
      if (isDeafened.value) return options.t('common.status.deafened')
      if (options.voiceRtc.isMuted.value) return options.t('common.status.muted')
      if (options.voiceRtc.localSpeaking.value) return options.t('voice.speaking')
      return options.t('common.status.connected')
    }
    return options.t('voice.selectToPreview')
  })

  async function loadVoiceConfig() {
    const config = await apiGet<VoiceConfig>('/api/meta/voice')
    voiceIceServers.value = config.ice_servers
    voiceTurnConfigured.value = config.turn_configured
  }

  function disconnectVoice() {
    if (options.guilds.connectedVoiceGuildId) {
      options.updateVoiceState({
        guild_id: options.guilds.connectedVoiceGuildId,
        channel_id: null,
        self_mute: false,
        self_deaf: false,
      })
    }
    options.voiceRtc.disconnect()
    options.guilds.setVoiceConnected(false)
  }

  function voiceParticipantsForChannel(channelId: number): VoiceState[] {
    return options.guilds.voiceStates.filter((state) => state.channel_id === channelId)
  }

  function findVoiceChannel(channelId: number): { guild: Guild; channel: Channel } | null {
    for (const guild of options.guilds.guilds) {
      const channel = guild.channels.find((item) => item.id === channelId && item.type === 1)
      if (channel) return { guild, channel }
    }
    return null
  }

  async function connectVoiceToChannel(channelId: number) {
    const user = options.session.user as User | null
    if (!user) return
    const target = findVoiceChannel(channelId)
    if (!target) return

    try {
      await options.voiceRtc.connect({
        channelId: target.channel.id,
        currentUserId: user.id,
        participants: voiceParticipantsForChannel(target.channel.id),
        iceServers: voiceIceServers.value,
        sendSignal: options.sendVoiceSignal,
      })
    } catch (error) {
      options.setError(error instanceof Error ? error.message : options.t('app.error.voiceConnectFailed'))
      return
    }

    options.guilds.setVoiceConnected(true, target.channel)
    options.updateVoiceState({
      guild_id: target.guild.id,
      channel_id: target.channel.id,
      self_mute: options.voiceRtc.isMuted.value,
      self_deaf: isDeafened.value,
    })
  }

  async function handleToggleVoice() {
    if (!options.activeGuild() || !options.guilds.voiceChannel || !options.session.user) return
    if (options.guilds.voiceConnected) {
      disconnectVoice()
      return
    }

    await connectVoiceToChannel(options.guilds.voiceChannel.id)
  }

  async function handleJoinVoiceChannel(channelId: number) {
    options.setError(null)
    options.guilds.selectChannel(channelId)
    if (connectedVoiceChannelId.value === channelId) return
    if (options.guilds.voiceConnected) {
      if (options.guilds.connectedVoiceGuildId !== options.activeGuild()?.id && !skipVoiceSwitchConfirm.value) {
        rememberVoiceSwitchChoice.value = false
        pendingVoiceSwitchChannelId.value = channelId
        return
      }
      disconnectVoice()
    }
    await connectVoiceToChannel(channelId)
  }

  async function confirmVoiceSwitch() {
    const channelId = pendingVoiceSwitchChannelId.value
    pendingVoiceSwitchChannelId.value = null
    if (!channelId) return
    if (rememberVoiceSwitchChoice.value) {
      skipVoiceSwitchConfirm.value = true
      browserStorage.setItem('discord_clone_skip_voice_switch_confirm', 'true')
    } else {
      browserStorage.removeItem('discord_clone_skip_voice_switch_confirm')
    }
    rememberVoiceSwitchChoice.value = false
    disconnectVoice()
    await connectVoiceToChannel(channelId)
  }

  function cancelVoiceSwitch() {
    rememberVoiceSwitchChoice.value = false
    pendingVoiceSwitchChannelId.value = null
  }

  function handleLeaveVoiceChannel(channelId: number) {
    options.setError(null)
    if (connectedVoiceChannelId.value !== channelId) return
    disconnectVoice()
  }

  function publishCurrentVoiceState() {
    if (!options.guilds.voiceConnected || !options.guilds.connectedVoiceGuildId || !options.guilds.connectedVoiceChannelId) return
    options.updateVoiceState({
      guild_id: options.guilds.connectedVoiceGuildId,
      channel_id: options.guilds.connectedVoiceChannelId,
      self_mute: options.voiceRtc.isMuted.value,
      self_deaf: isDeafened.value,
    })
  }

  function handleToggleDeafen() {
    isDeafened.value = !isDeafened.value
    publishCurrentVoiceState()
  }

  function handleToggleMute() {
    options.voiceRtc.toggleMute()
    publishCurrentVoiceState()
  }

  function handleToggleScreenShare() {
    options.setError(null)
    if (!options.guilds.voiceConnected) return
    void options.voiceRtc.toggleScreenShare().catch((error) => {
      options.setError(error instanceof Error ? error.message : options.t('app.error.screenShareFailed'))
    })
  }

  watch(
    () => options.guilds.connectedVoiceStates.map((state) => `${state.user_id}:${state.channel_id}`).join('|'),
    () => {
      if (!options.voiceRtc.isCapturing.value || !options.session.user) return
      void options.voiceRtc.syncParticipants(options.guilds.connectedVoiceStates).catch((error) => {
        options.setError(error instanceof Error ? error.message : options.t('app.error.voicePeerSyncFailed'))
      })
    },
  )

  watch(
    () => options.guilds.lastVoiceSignal,
    (signal: VoiceSignal | null) => {
      if (!signal) return
      void options.voiceRtc.handleSignal(signal).catch((error) => {
        options.setError(error instanceof Error ? error.message : options.t('app.error.voiceSignalFailed'))
      })
    },
  )

  return {
    isDeafened,
    pendingVoiceSwitchChannelId,
    rememberVoiceSwitchChoice,
    voiceTurnConfigured,
    connectedVoiceChannelId,
    activeGuildConnectedVoiceChannelId,
    voicePanelChannel,
    selectedVoiceChannel,
    selectedVoiceParticipants,
    selectedVoicePeers,
    selectedVoiceConnected,
    voiceWorkspaceStatus,
    loadVoiceConfig,
    disconnectVoice,
    handleToggleVoice,
    handleJoinVoiceChannel,
    confirmVoiceSwitch,
    cancelVoiceSwitch,
    handleLeaveVoiceChannel,
    handleToggleDeafen,
    handleToggleMute,
    handleToggleScreenShare,
  }
}
