import { computed, onBeforeUnmount, ref, watch } from 'vue'

import { apiGet } from '../services/api'
import { browserStorage } from '../services/browserApi'
import type { TranslationKey } from '../i18n'
import type { Channel, DirectMessage, Guild, User, VoiceConfig, VoiceIceServer, VoiceSignal, VoiceState } from '../types'
import type { useGateway } from './useGateway'
import type { useVoiceRtc } from './useVoiceRtc'
import type { useGuildStore } from '../stores/guilds'
import type { useSessionStore } from '../stores/session'

type GuildStore = ReturnType<typeof useGuildStore>
type SessionStore = ReturnType<typeof useSessionStore>
type VoiceRtc = ReturnType<typeof useVoiceRtc>
type Gateway = ReturnType<typeof useGateway>

const VOICE_REJOIN_STORAGE_KEY = 'discord_clone_voice_rejoin'
const DM_SOLO_AUTO_LEAVE_MS = 180_000

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

interface StoredVoiceRejoin {
  userId: number
  guildId: number
  channelId: number
}

export function useVoiceSessionController(options: VoiceSessionControllerOptions) {
  const isDeafened = ref(false)
  const pendingVoiceSwitchChannelId = ref<number | null>(null)
  const pendingVoiceRejoinChannelId = ref<number | null>(null)
  const isRejoiningVoice = ref(false)
  const skipVoiceSwitchConfirm = ref(browserStorage.getItem('discord_clone_skip_voice_switch_confirm') === 'true')
  const rememberVoiceSwitchChoice = ref(false)
  const voiceIceServers = ref<VoiceIceServer[]>([{ urls: 'stun:stun.l.google.com:19302' }])
  const voiceTurnConfigured = ref(false)
  const connectedDmId = ref<number | null>(null)
  const connectedDmName = ref<string | null>(null)
  let dmSoloAutoLeaveTimer: number | null = null

  const voiceConnected = computed(() => options.guilds.voiceConnected || connectedDmId.value !== null)
  const connectedVoiceChannelId = computed(() =>
    options.guilds.voiceConnected ? options.guilds.connectedVoiceChannelId : null,
  )
  const connectedVoiceRoomId = computed(() => connectedDmId.value ?? connectedVoiceChannelId.value)
  const connectedVoiceContextType = computed<'guild' | 'dm' | null>(() => {
    if (connectedDmId.value !== null) return 'dm'
    if (options.guilds.voiceConnected) return 'guild'
    return null
  })
  const activeGuildConnectedVoiceChannelId = computed(() =>
    options.guilds.connectedVoiceGuildId === options.activeGuild()?.id ? connectedVoiceChannelId.value : null,
  )
  const voicePanelChannel = computed<Channel | null>(() => {
    if (connectedDmId.value !== null) {
      return {
        id: connectedDmId.value,
        guild_id: 0,
        name: connectedDmName.value ?? options.t('app.status.directMessage'),
        type: 1,
        position: 0,
      }
    }
    return options.guilds.voiceConnected ? options.guilds.connectedVoiceChannel : options.guilds.voiceChannel
  })
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
  const connectedVoiceStates = computed(() => {
    if (connectedDmId.value !== null) {
      return options.guilds.voiceStates.filter(
        (state) => state.context_type === 'dm' && state.dm_id === connectedDmId.value,
      )
    }
    return options.guilds.connectedVoiceStates
  })
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
  const pendingVoiceRejoinSummary = computed(() => {
    if (!pendingVoiceRejoinChannelId.value) return null
    return findVoiceChannel(pendingVoiceRejoinChannelId.value)
  })

  async function loadVoiceConfig() {
    const config = await apiGet<VoiceConfig>('/api/meta/voice')
    voiceIceServers.value = config.ice_servers
    voiceTurnConfigured.value = config.turn_configured
  }

  function readStoredVoiceRejoin(): StoredVoiceRejoin | null {
    const rawValue = browserStorage.getItem(VOICE_REJOIN_STORAGE_KEY)
    if (!rawValue) return null
    try {
      const parsed = JSON.parse(rawValue) as Partial<StoredVoiceRejoin>
      if (
        typeof parsed.userId === 'number'
        && typeof parsed.guildId === 'number'
        && typeof parsed.channelId === 'number'
      ) {
        return {
          userId: parsed.userId,
          guildId: parsed.guildId,
          channelId: parsed.channelId,
        }
      }
    } catch {
      // Ignore malformed local recovery metadata and clear it below.
    }
    browserStorage.removeItem(VOICE_REJOIN_STORAGE_KEY)
    return null
  }

  function rememberVoiceChannel(target: { guild: Guild; channel: Channel }) {
    const userId = options.session.user?.id
    if (!userId) return
    browserStorage.setItem(VOICE_REJOIN_STORAGE_KEY, JSON.stringify({
      userId,
      guildId: target.guild.id,
      channelId: target.channel.id,
    }))
  }

  function clearVoiceRejoinRecovery() {
    pendingVoiceRejoinChannelId.value = null
    browserStorage.removeItem(VOICE_REJOIN_STORAGE_KEY)
  }

  function restoreVoiceRejoinPrompt() {
    const stored = readStoredVoiceRejoin()
    if (!stored) return
    if (options.guilds.voiceConnected || stored.userId !== options.session.user?.id) {
      clearVoiceRejoinRecovery()
      return
    }
    const target = findVoiceChannel(stored.channelId)
    if (!target || target.guild.id !== stored.guildId) {
      clearVoiceRejoinRecovery()
      return
    }
    pendingVoiceRejoinChannelId.value = stored.channelId
  }

  function dismissVoiceRejoin() {
    clearVoiceRejoinRecovery()
  }

  async function confirmVoiceRejoin() {
    const channelId = pendingVoiceRejoinChannelId.value
    pendingVoiceRejoinChannelId.value = null
    if (!channelId) return
    await connectVoiceToChannel(channelId)
    if (!options.guilds.voiceConnected) {
      pendingVoiceRejoinChannelId.value = channelId
    }
  }

  async function attemptAutomaticVoiceRejoin() {
    if (isRejoiningVoice.value || options.guilds.voiceConnected || !pendingVoiceRejoinChannelId.value) {
      return false
    }
    isRejoiningVoice.value = true
    try {
      await confirmVoiceRejoin()
      return options.guilds.voiceConnected
    } finally {
      isRejoiningVoice.value = false
    }
  }

  function disconnectVoice() {
    clearDmSoloAutoLeaveTimer()
    if (options.guilds.connectedVoiceGuildId) {
      options.updateVoiceState({
        context_type: 'guild',
        guild_id: options.guilds.connectedVoiceGuildId,
        channel_id: null,
        self_mute: false,
        self_deaf: false,
      })
    }
    if (connectedDmId.value !== null) {
      options.updateVoiceState({
        context_type: 'dm',
        guild_id: null,
        channel_id: null,
        dm_id: connectedDmId.value,
        self_mute: false,
        self_deaf: false,
      })
    }
    options.voiceRtc.disconnect()
    isDeafened.value = false
    options.guilds.setVoiceConnected(false)
    connectedDmId.value = null
    connectedDmName.value = null
    clearVoiceRejoinRecovery()
  }

  function voiceParticipantsForChannel(channelId: number): VoiceState[] {
    return options.guilds.voiceStates.filter(
      (state) => (state.context_type ?? 'guild') === 'guild' && state.channel_id === channelId,
    )
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
    if (connectedDmId.value !== null) disconnectVoice()

    try {
      await options.voiceRtc.connect({
        channelId: target.channel.id,
        currentUserId: user.id,
        participants: [],
        iceServers: voiceIceServers.value,
        sendSignal: options.sendVoiceSignal,
      })
    } catch (error) {
      options.setError(error instanceof Error ? error.message : options.t('app.error.voiceConnectFailed'))
      return
    }

    options.guilds.setVoiceConnected(true, target.channel)
    connectedDmId.value = null
    connectedDmName.value = null
    rememberVoiceChannel(target)
    options.updateVoiceState({
      context_type: 'guild',
      guild_id: target.guild.id,
      channel_id: target.channel.id,
      session_id: options.voiceRtc.getSessionId(),
      self_mute: options.voiceRtc.isMuted.value,
      self_deaf: isDeafened.value,
    })
  }

  async function connectVoiceToDm(dm: DirectMessage) {
    const user = options.session.user as User | null
    if (!user) return
    if (connectedDmId.value === dm.id) return
    if (voiceConnected.value) disconnectVoice()

    try {
      await options.voiceRtc.connect({
        channelId: dm.id,
        currentUserId: user.id,
        participants: [],
        iceServers: voiceIceServers.value,
        sendSignal: (payload) => options.sendVoiceSignal({
          ...payload,
          context_type: 'dm',
          dm_id: dm.id,
          channel_id: dm.id,
        }),
      })
    } catch (error) {
      options.setError(error instanceof Error ? error.message : options.t('app.error.voiceConnectFailed'))
      return
    }

    options.guilds.setVoiceConnected(false)
    connectedDmId.value = dm.id
    connectedDmName.value = dm.display_name
    clearVoiceRejoinRecovery()
    options.updateVoiceState({
      context_type: 'dm',
      guild_id: null,
      channel_id: dm.id,
      dm_id: dm.id,
      session_id: options.voiceRtc.getSessionId(),
      self_mute: options.voiceRtc.isMuted.value,
      self_deaf: isDeafened.value,
    })
  }

  async function handleToggleVoice() {
    if (voiceConnected.value) {
      disconnectVoice()
      return
    }
    if (!options.activeGuild() || !options.guilds.voiceChannel || !options.session.user) return

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
    if (connectedDmId.value !== null) {
      options.updateVoiceState({
        context_type: 'dm',
        guild_id: null,
        channel_id: connectedDmId.value,
        dm_id: connectedDmId.value,
        session_id: options.voiceRtc.getSessionId(),
        self_mute: options.voiceRtc.isMuted.value,
        self_deaf: isDeafened.value,
      })
      return
    }
    if (!options.guilds.voiceConnected || !options.guilds.connectedVoiceGuildId || !options.guilds.connectedVoiceChannelId) return
    options.updateVoiceState({
      context_type: 'guild',
      guild_id: options.guilds.connectedVoiceGuildId,
      channel_id: options.guilds.connectedVoiceChannelId,
      session_id: options.voiceRtc.getSessionId(),
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
    if (!voiceConnected.value) return
    void options.voiceRtc.toggleScreenShare().catch((error) => {
      options.setError(error instanceof Error ? error.message : options.t('app.error.screenShareFailed'))
    })
  }

  function clearDmSoloAutoLeaveTimer() {
    if (dmSoloAutoLeaveTimer === null) return
    window.clearTimeout(dmSoloAutoLeaveTimer)
    dmSoloAutoLeaveTimer = null
  }

  function scheduleDmSoloAutoLeaveIfNeeded() {
    clearDmSoloAutoLeaveTimer()
    const userId = options.session.user?.id
    if (!userId || connectedDmId.value === null || !options.voiceRtc.isCapturing.value) return
    const participants = connectedVoiceStates.value
    const localParticipantPresent = participants.some((state) => state.user_id === userId)
    const remoteParticipantCount = participants.filter((state) => state.user_id !== userId).length
    if (!localParticipantPresent || remoteParticipantCount > 0) return
    dmSoloAutoLeaveTimer = window.setTimeout(() => {
      dmSoloAutoLeaveTimer = null
      if (connectedDmId.value === null) return
      const currentParticipants = connectedVoiceStates.value
      const currentRemoteCount = currentParticipants.filter((state) => state.user_id !== userId).length
      if (currentRemoteCount === 0) disconnectVoice()
    }, DM_SOLO_AUTO_LEAVE_MS)
  }

  watch(
    () => connectedVoiceStates.value.map((state) =>
      `${state.context_type ?? 'guild'}:${state.dm_id ?? state.channel_id}:${state.user_id}:${state.session_id ?? ''}`,
    ).join('|'),
    () => {
      if (!options.voiceRtc.isCapturing.value || !options.session.user) return
      void options.voiceRtc.syncParticipants(connectedVoiceStates.value).catch((error) => {
        options.setError(error instanceof Error ? error.message : options.t('app.error.voicePeerSyncFailed'))
      })
    },
  )

  watch(
    () => [
      connectedDmId.value,
      options.voiceRtc.isCapturing.value,
      connectedVoiceStates.value.map((state) => state.user_id).sort((a, b) => a - b).join('|'),
    ].join(':'),
    scheduleDmSoloAutoLeaveIfNeeded,
  )

  watch(
    () => options.guilds.lastVoiceSignal,
    (signal: VoiceSignal | null) => {
      if (!signal) return
      const contextType = signal.context_type ?? 'guild'
      const signalRoomId = contextType === 'dm' ? signal.dm_id : signal.channel_id
      if (contextType !== connectedVoiceContextType.value || signalRoomId !== connectedVoiceRoomId.value) return
      void options.voiceRtc.handleSignal(signal).catch((error) => {
        options.setError(error instanceof Error ? error.message : options.t('app.error.voiceSignalFailed'))
      })
    },
  )

  onBeforeUnmount(() => {
    clearDmSoloAutoLeaveTimer()
  })

  return {
    isDeafened,
    pendingVoiceSwitchChannelId,
    pendingVoiceRejoinChannelId,
    pendingVoiceRejoinSummary,
    rememberVoiceSwitchChoice,
    voiceTurnConfigured,
    voiceConnected,
    connectedDmId,
    connectedDmName,
    connectedVoiceChannelId,
    connectedVoiceRoomId,
    activeGuildConnectedVoiceChannelId,
    voicePanelChannel,
    selectedVoiceChannel,
    selectedVoiceParticipants,
    selectedVoicePeers,
    selectedVoiceConnected,
    voiceWorkspaceStatus,
    loadVoiceConfig,
    restoreVoiceRejoinPrompt,
    attemptAutomaticVoiceRejoin,
    confirmVoiceRejoin,
    dismissVoiceRejoin,
    disconnectVoice,
    connectVoiceToDm,
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
