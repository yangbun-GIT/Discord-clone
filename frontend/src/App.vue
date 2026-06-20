<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  BellOff,
  Bell,
  Hash,
  Link,
  MessageCircle,
  Mic,
  Pin,
  Phone,
  Radio,
  Search,
  Settings,
  PhoneOff,
  ScreenShare,
  ScreenShareOff,
  UserRound,
  Users,
  X,
} from 'lucide-vue-next'

import AuthPanel from './components/AuthPanel.vue'
import ChannelSidebar from './components/ChannelSidebar.vue'
import ChatView from './components/ChatView.vue'
import CreateDmDialog from './components/CreateDmDialog.vue'
import DirectMessageView from './components/DirectMessageView.vue'
import FriendProfileDialog from './components/FriendProfileDialog.vue'
import FriendsHome from './components/FriendsHome.vue'
import MemberList from './components/MemberList.vue'
import PrivateChannelSidebar from './components/PrivateChannelSidebar.vue'
import ServerAddDialog from './components/ServerAddDialog.vue'
import ServerDiscoveryDialog from './components/ServerDiscoveryDialog.vue'
import ServerRail from './components/ServerRail.vue'
import SettingsView from './components/SettingsView.vue'
import VoiceAudioSink from './components/VoiceAudioSink.vue'
import VoicePanel from './components/VoicePanel.vue'
import VoiceVideoSink from './components/VoiceVideoSink.vue'
import { useContextMenuController } from './composables/useContextMenuController'
import { useGateway } from './composables/useGateway'
import { useGlobalNotice } from './composables/useGlobalNotice'
import { useInviteController } from './composables/useInviteController'
import { useVoiceRtc } from './composables/useVoiceRtc'
import { useVoiceSessionController } from './composables/useVoiceSessionController'
import { useWorkspaceController } from './composables/useWorkspaceController'
import type { VoiceMediaErrorCode } from './composables/voiceMedia'
import { useI18n, type TranslationKey } from './i18n'
import {
  addDocumentEventListener,
  getCurrentHref,
  getViewportSize,
  writeClipboardText,
} from './services/browserApi'
import { useDmStore } from './stores/dms'
import { useGuildStore } from './stores/guilds'
import { useNavigationStore, type PersistedWorkspaceLocation } from './stores/navigation'
import { usePreferencesStore } from './stores/preferences'
import { useSessionStore } from './stores/session'
import { useStoreStore } from './stores/store'
import type { ServerRailGuildMeta, UserPresenceStatus } from './types'

const session = useSessionStore()
const guilds = useGuildStore()
const dms = useDmStore()
const navigation = useNavigationStore()
const preferences = usePreferencesStore()
const store = useStoreStore()
const { t } = useI18n()
const {
  connect: connectGateway,
  disconnect: disconnectGateway,
  updateVoiceState,
  sendVoiceSignal,
  updatePresence,
  status: gatewayStatus,
} = useGateway()
const voiceRtc = useVoiceRtc()
const settingsInitialPanel = ref<'account' | 'voice'>('account')
let removeDocumentKeyDown: (() => void) | null = null

const activeGuild = computed(() => guilds.activeGuild)
const activeChannel = computed(() => guilds.activeChannel)
const activeMessages = computed(() => guilds.activeMessages)
const activeRemoteVoiceStreams = computed(() =>
  voiceRtc.remoteStreams.value.filter((remote) => remote.channelId === connectedVoiceRoomId.value),
)
const remoteScreenStreams = computed(() =>
  activeRemoteVoiceStreams.value.filter((remote) => remote.sharingScreen),
)
const remoteScreenUserIds = computed(() => new Set(remoteScreenStreams.value.map((remote) => remote.userId)))
const remoteVoiceStreamByUserId = computed(() =>
  new Map(activeRemoteVoiceStreams.value.map((remote) => [remote.userId, remote])),
)
const visibleSelectedVoicePeers = computed(() =>
  selectedVoicePeers.value.filter((participant) => !remoteScreenUserIds.value.has(participant.user_id)),
)
const voiceLocationSummary = computed(() => {
  if (connectedDmId.value !== null) {
    const state = isDeafened.value
      ? t('common.status.deafened')
      : voiceRtc.isMuted.value
        ? t('common.status.muted')
        : voiceRtc.localSpeaking.value
          ? t('voice.speaking')
          : t('common.status.connected')
    return `${t('app.status.directMessage')} / ${connectedDmName.value ?? selectedDm.value?.display_name ?? ''} 쨌 ${state}`
  }
  if (!guilds.voiceConnected || !guilds.connectedVoiceChannel || !guilds.connectedVoiceGuild) return null
  const state = isDeafened.value
    ? t('common.status.deafened')
    : voiceRtc.isMuted.value
      ? t('common.status.muted')
      : voiceRtc.localSpeaking.value
        ? t('voice.speaking')
        : t('common.status.connected')
  return `${guilds.connectedVoiceGuild.name} / ${guilds.connectedVoiceChannel.name} · ${state}`
})
const voiceErrorMessage = computed(() => {
  if (!voiceRtc.errorCode.value) return voiceRtc.error.value
  return t(voiceMediaErrorKey(voiceRtc.errorCode.value))
})
const isPrivateDestination = computed(() =>
  navigation.destination === 'friends' || navigation.destination === 'dm',
)
const isServerDestination = computed(() =>
  navigation.destination === 'server_channel' || navigation.destination === 'voice_channel',
)
const showWorkspaceTopbar = computed(() => navigation.destination !== 'friends')
const voiceConnectedElsewhere = computed(() =>
  Boolean(guilds.voiceConnected && activeGuild.value && guilds.connectedVoiceGuildId !== activeGuild.value.id),
)
const localMicrophoneTracksMuted = computed(() => {
  const tracks = voiceRtc.localStream.value?.getAudioTracks() ?? []
  return voiceRtc.isMuted.value && tracks.length > 0 && tracks.every((track) => !track.enabled)
})
const selectedDm = computed(() => dms.getDm(navigation.activeDmId))
const selectedDmMuted = computed(() => preferences.isDmMuted(selectedDm.value?.id ?? null))
const isBooting = ref(true)
const authError = ref<string | null>(null)
const workspaceError = ref<string | null>(null)
const {
  notice: workspaceNotice,
  tone: workspaceNoticeTone,
  setNotice: setWorkspaceNotice,
  clearNotice: clearWorkspaceNotice,
} = useGlobalNotice({
  onShow: () => {
    workspaceError.value = null
  },
})
const isAuthenticating = ref(false)
const isCreatingGuild = ref(false)
const isInviteWorking = ref(false)
const activeHeaderPanel = ref<'threads' | 'notifications' | 'pins' | 'search' | null>(null)
const notificationMode = ref<'all' | 'mentions' | 'none'>('all')
const channelSearchQuery = ref('')
const showAddServer = ref(false)
const addServerMode = ref<'create' | 'join'>('create')
const showDiscovery = ref(false)
const showMemberList = ref(true)
const {
  showInvite,
  inviteCode,
  inviteSearchQuery,
  inviteCodeCopied,
  inviteFriends,
  inviteFriendState,
  openInvite,
  closeInvite,
  setInviteCodeCopied,
  setInviteFriendState,
} = useInviteController(() => dms.relationships)
const {
  menu: globalContextMenu,
  openMenu: openContextMenu,
  closeMenu: closeGlobalContextMenu,
} = useContextMenuController()
const userPresenceStatus = ref<UserPresenceStatus>('online')
const showCreateDmDialog = ref(false)
const profileFriendId = ref<number | null>(null)
const pendingRequestFocusKey = ref(0)
const friendsHomeResetKey = ref(0)
const activeContextTarget = ref<{ kind: string; id: number | null; label: string } | null>(null)
const profileFriend = computed(() =>
  profileFriendId.value === null
    ? null
    : dms.relationships.find((friend) => friend.id === profileFriendId.value) ?? null,
)
const {
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
} = useVoiceSessionController({
  guilds,
  session,
  voiceRtc,
  activeGuild: () => activeGuild.value,
  activeChannel: () => activeChannel.value,
  updateVoiceState,
  sendVoiceSignal,
  setError: (message) => {
    workspaceError.value = message
  },
  t,
})
const dismissedIncomingDmCallKeys = ref<string[]>([])
const selectedDmCallJoinable = computed(() => {
  const currentUserId = session.user?.id ?? null
  const dm = selectedDm.value
  if (!dm || currentUserId === null || connectedDmId.value === dm.id) return false
  return guilds.voiceStates.some((state) =>
    (state.context_type ?? 'guild') === 'dm'
    && state.dm_id === dm.id
    && state.user_id !== currentUserId,
  )
})
const incomingDmCall = computed(() => {
  const currentUserId = session.user?.id ?? null
  if (currentUserId === null) return null
  for (const state of guilds.voiceStates) {
    if ((state.context_type ?? 'guild') !== 'dm') continue
    if (state.dm_id === null || typeof state.dm_id === 'undefined') continue
    if (state.user_id === currentUserId) continue
    if (connectedDmId.value === state.dm_id) continue
    const key = `${state.dm_id}:${state.user_id}`
    if (dismissedIncomingDmCallKeys.value.includes(key)) continue
    const dm = dms.getDm(state.dm_id)
    if (!dm) continue
    return {
      key,
      dm,
      callerName: state.username ?? dm.display_name,
    }
  }
  return null
})
watch(
  () => guilds.voiceStates
    .filter((state) => (state.context_type ?? 'guild') === 'dm' && typeof state.dm_id === 'number')
    .map((state) => `${state.dm_id}:${state.user_id}`)
    .join('|'),
  (activeKeys) => {
    const activeKeySet = new Set(activeKeys ? activeKeys.split('|') : [])
    dismissedIncomingDmCallKeys.value = dismissedIncomingDmCallKeys.value.filter((key) => activeKeySet.has(key))
  },
)
watch(
  connectedDmId,
  (currentDmId, previousDmId) => {
    if (currentDmId !== null || previousDmId === null) return
    dismissActiveRemoteDmCallKeys(previousDmId)
  },
)
const { workspaceTitle, workspaceSubtitle } = useWorkspaceController({
  destination: () => navigation.destination,
  activeGuild: () => activeGuild.value ?? null,
  activeChannel: () => activeChannel.value ?? null,
  selectedDm: () => selectedDm.value,
  voiceConnected: () => voiceConnected.value,
  connectedVoiceGuild: () => guilds.connectedVoiceGuild,
  connectedVoiceChannel: () => guilds.connectedVoiceChannel,
  isDeafened: () => isDeafened.value,
  isMuted: () => voiceRtc.isMuted.value,
  localSpeaking: () => voiceRtc.localSpeaking.value,
  t,
})
const serverRailMeta = computed<Record<number, ServerRailGuildMeta>>(() => {
  const entries = guilds.guilds.map((guild, index) => {
    const unreadCount = activeGuild.value?.id === guild.id ? 0 : Math.min(guild.messages.length, 9)
    return [
      guild.id,
      {
        unread_count: unreadCount,
        mention_count: index === 0 && !isPrivateDestination.value ? 0 : Number(index === 0 && unreadCount > 0),
        muted: index % 3 === 2,
        voice_connected: guilds.voiceConnected && guilds.connectedVoiceGuildId === guild.id,
        folder_name: index < 2 ? 'Project' : null,
        folder_color: index < 2 ? '#5eead4' : null,
      },
    ] as const
  })
  return Object.fromEntries(entries)
})
const channelSearchResults = computed(() => {
  const query = channelSearchQuery.value.trim().toLowerCase()
  if (!query) return []
  return activeMessages.value.filter((message) =>
    message.content.toLowerCase().includes(query)
    || message.author_name.toLowerCase().includes(query),
  )
})

watch(
  () => [
    navigation.destination,
    navigation.activeDmId,
    guilds.activeGuildId,
    guilds.activeChannelId,
  ],
  () => {
    closeGlobalContextMenu()
    activeHeaderPanel.value = null
    if (isBooting.value || !session.user) return
    navigation.persistWorkspaceLocation(session.user.id, guilds.activeGuildId, guilds.activeChannelId)
  },
)

watch(
  () => navigation.activeDmId,
  (dmId) => {
    dms.setActiveDm(dmId)
  },
  { immediate: true },
)

watch(
  () => session.user?.id ?? null,
  (userId) => {
    dms.setCurrentUserId(userId)
  },
  { immediate: true },
)

watch(
  () => [gatewayStatus.value, pendingVoiceRejoinChannelId.value] as const,
  ([status, rejoinChannelId]) => {
    if (status !== 'connected' || !rejoinChannelId) return
    void attemptAutomaticVoiceRejoin()
  },
)

watch(
  () => gatewayStatus.value,
  (status) => {
    if (status !== 'connected' || !session.user) return
    updatePresence({ status: userPresenceStatus.value, activity: null })
  },
)

async function openWorkspace() {
  if (!session.token || !session.user) return
  const restoredLocation = navigation.readPersistedWorkspaceLocation(session.user.id)
  prepareWorkspaceLocationRestore(restoredLocation)
  await reloadWorkspaceState()
  restoreVoiceRejoinPrompt()
  restoreWorkspaceLocation(restoredLocation)
  connectGateway(session.token, {
    onDispatch: (event, data) => {
      const previousIncomingRequestIds = new Set(
        dms.relationships
          .filter((friend) => friend.relationship === 'pending_incoming')
          .map((friend) => friend.id),
      )
      guilds.handleGatewayDispatch(event, data)
      dms.handleGatewayDispatch(event, data)
      if (
        event === 'RELATIONSHIP_UPDATE'
        && typeof data.id === 'number'
        && data.relationship === 'pending_incoming'
        && !previousIncomingRequestIds.has(data.id)
      ) {
        setWorkspaceNotice(t('friends.requestReceived', { username: String(data.username ?? t('friends.friend')) }), 'success')
        pendingRequestFocusKey.value += 1
      }
    },
    onReconnect: async () => {
      await reloadWorkspaceState()
      updatePresence({ status: userPresenceStatus.value, activity: null })
    },
  })
}

function prepareWorkspaceLocationRestore(location: PersistedWorkspaceLocation | null) {
  if (!location) return
  if (location.destination !== 'server_channel' && location.destination !== 'voice_channel') return
  guilds.activeGuildId = location.activeGuildId
  guilds.activeChannelId = location.activeChannelId
}

function restoreWorkspaceLocation(location: PersistedWorkspaceLocation | null) {
  if (!location) {
    navigation.openFriends()
    return
  }

  if (location.destination === 'dm') {
    const dmId = location.activeDmId
    if (dmId && dms.getDm(dmId)) {
      navigation.openDm(dmId)
      return
    }
    navigation.openFriends()
    return
  }

  if (location.destination === 'server_channel' || location.destination === 'voice_channel') {
    if (guilds.activeGuild && guilds.activeChannel) {
      if (location.destination === 'voice_channel' && guilds.activeChannel.type === 1) {
        navigation.openVoiceChannel()
      } else {
        navigation.openServerChannel()
      }
      return
    }
  }

  navigation.openFriends()
}

async function reloadWorkspaceState() {
  if (!session.token) return
  await Promise.all([
    guilds.loadGuilds(session.token),
    dms.loadPrivateWorkspace(session.token),
    loadVoiceConfig(),
  ])
}

onMounted(async () => {
  preferences.restorePreferences()
  void voiceRtc.refreshVoiceDevices()
  await session.restoreSession()
  if (session.token) {
    await openWorkspace()
  }
  removeDocumentKeyDown = addDocumentEventListener('keydown', handleDocumentKeyDown)
  isBooting.value = false
})

onBeforeUnmount(() => {
  removeDocumentKeyDown?.()
  removeDocumentKeyDown = null
  clearWorkspaceNotice()
})

function contextMenuItems(kind: string) {
  const inviteMenuItems = guilds.canCreateInvite
    ? [{ id: 'invite', label: t('channel.menu.invitePeople') }]
    : []

  if (kind === 'message' || kind === 'dm-message') {
    return [
      { id: 'reply', label: t('context.reply') },
      { id: 'copy-message', label: t('context.copyMessage') },
      { id: 'edit-message', label: t('context.editMessage') },
      { id: 'pin-message', label: t('context.pinMessage') },
    ]
  }
  if (kind === 'friend' || kind === 'dm-row') {
    return [
      { id: 'view-profile', label: t('friends.viewProfile') },
      { id: 'message-friend', label: t('friends.sendMessage') },
      { id: 'start-dm-call', label: t('friends.startCall') },
      { id: 'mute-dm', label: t('friends.muteConversation') },
    ]
  }
  if (kind === 'user-panel') {
    return [
      { id: 'open-settings', label: t('settings.userSettings') },
    ]
  }
  if (kind === 'voice-channel' || kind === 'voice-session') {
    return [
      { id: guilds.voiceConnected ? 'voice-disconnect' : 'voice-connect', label: guilds.voiceConnected ? t('voice.disconnect') : t('voice.joinSelected') },
      ...inviteMenuItems,
      { id: 'copy-link', label: t('context.copyChannelLink') },
      { id: 'settings', label: t('channel.aria.settings') },
    ]
  }
  if (kind === 'text-channel') {
    return [
      { id: 'mark-read', label: t('context.markRead') },
      ...inviteMenuItems,
      { id: 'copy-link', label: t('context.copyChannelLink') },
      { id: 'settings', label: t('channel.aria.settings') },
    ]
  }
  if (kind === 'server') {
    return [
      { id: 'mark-read', label: t('context.markRead') },
      ...inviteMenuItems,
      { id: 'settings', label: t('channel.menu.serverSettings') },
    ]
  }
  return [
    { id: 'mark-read', label: t('context.markRead') },
    { id: 'open-settings', label: t('settings.userSettings') },
  ]
}

function openGlobalContextMenu(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (target.closest('.friend-local-menu, .server-context-menu, .global-context-menu')) return

  const contextElement = target.closest<HTMLElement>('[data-context-kind]')
  const kind = contextElement?.dataset.contextKind ?? 'workspace'
  const label = contextElement?.dataset.contextLabel ?? workspaceTitle.value
  const id = Number(contextElement?.dataset.contextId)
  activeContextTarget.value = {
    kind,
    id: Number.isSafeInteger(id) ? id : null,
    label,
  }
  const items = contextMenuItems(kind)
  if (!items.length) return
  const menuWidth = 244
  const menuHeight = 228
  const viewport = getViewportSize()

  openContextMenu({
    x: Math.max(8, Math.min(event.clientX, viewport.width - menuWidth - 8)),
    y: Math.max(8, Math.min(event.clientY, viewport.height - menuHeight - 8)),
    title: label,
    items,
  })
}

function runGlobalContextAction(id: string) {
  const actionLabel = globalContextMenu.value?.items.find((item) => item.id === id)?.label ?? globalContextMenu.value?.title ?? ''
  if (id === 'invite') {
    void handleCreateInvite()
  } else if (id === 'view-profile') {
    handleViewContextProfile()
  } else if (id === 'message-friend') {
    void handleMessageContextTarget()
  } else if (id === 'start-dm-call') {
    void handleStartContextCall()
  } else if (id === 'mute-dm') {
    void handleToggleContextMute()
  } else if (id === 'settings' || id === 'open-settings') {
    handleOpenUserSettings()
  } else if (id === 'voice-disconnect') {
    disconnectVoice()
  } else if (id === 'copy-message' || id === 'copy-link') {
    const value = id === 'copy-link' ? getCurrentHref() : globalContextMenu.value?.title ?? ''
    void copyToClipboard(value, t('app.notice.copySuccess'), t('app.notice.copyFailed'))
  } else {
    setWorkspaceNotice(t('app.notice.localControl', { label: actionLabel }))
  }
  activeContextTarget.value = null
  closeGlobalContextMenu()
}

function handleWorkspacePointerDown(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (globalContextMenu.value && !target.closest('.global-context-menu')) {
    closeGlobalContextMenu()
  }
  if (workspaceNotice.value && !target.closest('.app-notice')) {
    clearWorkspaceNotice()
  }
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return
  if (pendingVoiceRejoinChannelId.value) dismissVoiceRejoin()
  if (pendingVoiceSwitchChannelId.value) cancelVoiceSwitch()
  closeGlobalContextMenu()
  if (workspaceNotice.value) clearWorkspaceNotice()
}

async function handleConfirmVoiceRejoin() {
  const target = pendingVoiceRejoinSummary.value
  if (target) {
    guilds.selectGuild(target.guild.id)
    guilds.selectChannel(target.channel.id)
    navigation.openVoiceChannel()
  }
  await confirmVoiceRejoin()
}

async function runAuth(action: () => Promise<void>) {
  authError.value = null
  isAuthenticating.value = true
  try {
      await action()
      await openWorkspace()
  } catch (error) {
    authError.value = error instanceof Error ? error.message : t('app.error.authFailed')
  } finally {
    isAuthenticating.value = false
  }
}

function handleLogin(payload: { username: string; password: string }) {
  void runAuth(() => session.login(payload))
}

function handleRegister(payload: { username: string; password: string }) {
  void runAuth(() => session.register(payload))
}

function handleDemo() {
  void runAuth(() => session.ensureDevSession())
}

function handleLogout() {
  disconnectVoice()
  dismissVoiceRejoin()
  disconnectGateway()
  authError.value = null
  workspaceError.value = null
  clearWorkspaceNotice()
  session.logout()
  navigation.clearPersistedWorkspaceLocation()
  navigation.resetNavigation()
  guilds.resetGuilds()
  dms.resetDms()
  store.resetStoreState()
  userPresenceStatus.value = 'online'
  isDeafened.value = false
}

function voiceMediaErrorKey(errorCode: VoiceMediaErrorCode): TranslationKey {
  switch (errorCode) {
    case 'media-unsupported':
      return 'voice.error.mediaUnsupported'
    case 'insecure-context':
      return 'voice.error.insecureContext'
    case 'permission-denied':
      return 'voice.error.permissionDenied'
    case 'no-device':
      return 'voice.error.noDevice'
    case 'device-busy':
      return 'voice.error.deviceBusy'
    case 'constraints-unsatisfied':
      return 'voice.error.constraints'
    case 'permission-timeout':
      return 'voice.error.permissionTimeout'
    case 'screen-permission-denied':
      return 'voice.error.screenPermissionDenied'
    case 'screen-unavailable':
      return 'voice.error.screenUnavailable'
    case 'screen-timeout':
      return 'voice.error.screenTimeout'
    case 'unknown':
    default:
      return 'voice.error.unknown'
  }
}

function handleRetryVoiceCapture() {
  const code = voiceRtc.errorCode.value
  if (code?.startsWith('screen') && voiceConnected.value) {
    handleToggleScreenShare()
    return
  }
  if (!voiceConnected.value) {
    void handleToggleVoice()
    return
  }
  if (connectedDmId.value !== null) {
    const dm = selectedDm.value?.id === connectedDmId.value ? selectedDm.value : dms.getDm(connectedDmId.value)
    if (!dm) return
    disconnectVoice()
    void connectVoiceToDm(dm)
    return
  }
  const channelId = guilds.connectedVoiceChannelId
  if (!channelId) return
  disconnectVoice()
  void handleJoinVoiceChannel(channelId)
}

function handleLeaveVoiceFromError() {
  if (voiceConnected.value) {
    disconnectVoice()
    return
  }
  if (guilds.connectedVoiceChannelId) {
    handleLeaveVoiceChannel(guilds.connectedVoiceChannelId)
    return
  }
  voiceRtc.disconnect()
}

function handleSelectGuild(guildId: number) {
  clearWorkspaceNotice()
  activeHeaderPanel.value = null
  navigation.openServerChannel()
  guilds.selectGuild(guildId)
}

function handleOpenFriends() {
  clearWorkspaceNotice()
  activeHeaderPanel.value = null
  friendsHomeResetKey.value += 1
  navigation.openFriends()
}

function handleOpenDm(dmId: number) {
  clearWorkspaceNotice()
  activeHeaderPanel.value = null
  navigation.openDm(dmId)
}

function handleCloseDm(dmId: number) {
  workspaceError.value = null
  void dms.closeDm(session.token, dmId)
    .then(() => {
      if (navigation.activeDmId === dmId) {
        navigation.openFriends()
      }
      setWorkspaceNotice(t('dm.closeSuccess'), 'success')
    })
    .catch((error) => {
      workspaceError.value = error instanceof Error ? error.message : t('app.error.dmCloseFailed')
    })
}

async function handleMessageFriend(friendId: number) {
  workspaceError.value = null
  try {
    const dm = await dms.createDm(session.token, [friendId])
    if (dm) {
      navigation.openDm(dm.id)
    }
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.dmCreateFailed')
  }
}

function friendFromContextTarget() {
  const target = activeContextTarget.value
  if (!target) return null
  if (target.kind === 'friend' && target.id !== null) {
    return dms.relationships.find((friend) => friend.id === target.id) ?? null
  }
  if (target.kind === 'dm-row' && target.id !== null) {
    const dm = dms.getDm(target.id)
    const recipientId = dm?.recipient_ids[0]
    return recipientId ? dms.relationships.find((friend) => friend.id === recipientId) ?? null : null
  }
  return null
}

function dmIdFromContextTarget() {
  const target = activeContextTarget.value
  if (!target) return null
  if (target.kind === 'dm-row') return target.id
  if (target.kind === 'friend' && target.id !== null) {
    return dms.dms.find((dm) => dm.recipient_ids.length === 1 && dm.recipient_ids[0] === target.id)?.id ?? null
  }
  return null
}

function handleViewProfile(friendId: number) {
  profileFriendId.value = friendId
}

function handleViewContextProfile() {
  const friend = friendFromContextTarget()
  if (friend) handleViewProfile(friend.id)
}

async function handleMessageContextTarget() {
  const target = activeContextTarget.value
  if (!target || target.id === null) return
  if (target.kind === 'dm-row') {
    navigation.openDm(target.id)
    return
  }
  if (target.kind === 'friend') {
    await handleMessageFriend(target.id)
  }
}

async function handleStartFriendCall(friendId: number) {
  workspaceError.value = null
  try {
    const dm = await dms.createDm(session.token, [friendId])
    if (!dm) return
    navigation.openDm(dm.id)
    await connectVoiceToDm(dm)
    setWorkspaceNotice(t('friends.dmCallStarted', { target: dm.display_name }), 'success')
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.voiceConnectFailed')
  }
}

async function handleAcceptIncomingDmCall() {
  const call = incomingDmCall.value
  if (!call) return
  dismissedIncomingDmCallKeys.value = dismissedIncomingDmCallKeys.value.filter((key) => key !== call.key)
  navigation.openDm(call.dm.id)
  await connectVoiceToDm(call.dm)
  setWorkspaceNotice(t('friends.dmCallAccepted', { target: call.callerName }), 'success')
}

function handleDismissIncomingDmCall() {
  const call = incomingDmCall.value
  if (!call) return
  dismissedIncomingDmCallKeys.value = Array.from(new Set([...dismissedIncomingDmCallKeys.value, call.key]))
}

function dismissActiveRemoteDmCallKeys(dmId: number) {
  const currentUserId = session.user?.id ?? null
  if (currentUserId === null) return
  const keys = guilds.voiceStates
    .filter((state) =>
      (state.context_type ?? 'guild') === 'dm'
      && state.dm_id === dmId
      && state.user_id !== currentUserId,
    )
    .map((state) => `${state.dm_id}:${state.user_id}`)
  if (!keys.length) return
  dismissedIncomingDmCallKeys.value = Array.from(new Set([...dismissedIncomingDmCallKeys.value, ...keys]))
}

async function handleStartContextCall() {
  const friend = friendFromContextTarget()
  if (!friend) return
  await handleStartFriendCall(friend.id)
}

async function handleStartSelectedDmCall() {
  if (!selectedDm.value) return
  await connectVoiceToDm(selectedDm.value)
  setWorkspaceNotice(t('friends.dmCallStarted', { target: selectedDm.value.display_name }), 'success')
}

function handleViewSelectedDmProfile() {
  const friendId = selectedDm.value?.recipient_ids[0]
  if (friendId) handleViewProfile(friendId)
}

async function handleToggleFriendMute(friendId: number) {
  const existingDmId = dms.dms.find((dm) => dm.recipient_ids.length === 1 && dm.recipient_ids[0] === friendId)?.id
  const dmId = existingDmId ?? (await dms.createDm(session.token, [friendId]))?.id ?? null
  if (!dmId) return
  preferences.toggleDmMuted(dmId)
  setWorkspaceNotice(
    preferences.isDmMuted(dmId) ? t('friends.conversationMuted') : t('friends.conversationUnmuted'),
    'success',
  )
}

async function handleToggleContextMute() {
  const dmId = dmIdFromContextTarget()
  if (dmId !== null) {
    preferences.toggleDmMuted(dmId)
    setWorkspaceNotice(
      preferences.isDmMuted(dmId) ? t('friends.conversationMuted') : t('friends.conversationUnmuted'),
      'success',
    )
    return
  }
  const friend = friendFromContextTarget()
  if (friend) await handleToggleFriendMute(friend.id)
}

function handleToggleSelectedDmMute() {
  const dmId = selectedDm.value?.id
  if (!dmId) return
  preferences.toggleDmMuted(dmId)
  setWorkspaceNotice(
    preferences.isDmMuted(dmId) ? t('friends.conversationMuted') : t('friends.conversationUnmuted'),
    'success',
  )
}

async function handleCreateDm(recipientIds: number[]) {
  workspaceError.value = null
  try {
    const dm = await dms.createDm(session.token, recipientIds)
    if (dm) {
      showCreateDmDialog.value = false
      navigation.openDm(dm.id)
      setWorkspaceNotice(t('dm.createSuccess'), 'success')
    }
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.dmCreateFailed')
  }
}

function handleFocusFriendRequests() {
  pendingRequestFocusKey.value += 1
  navigation.openFriends()
}

async function runRelationshipMutation(
  action: () => Promise<unknown>,
  successMessage: string,
) {
  workspaceError.value = null
  try {
    await action()
    setWorkspaceNotice(successMessage, 'success')
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.relationshipFailed')
  }
}

function handleAddFriend(username: string) {
  void runRelationshipMutation(
    () => dms.sendFriendRequest(session.token, username),
    t('friends.requestSent'),
  )
}

function handleAcceptFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.acceptRequest(session.token, friendId),
    t('friends.requestAccepted'),
  )
}

function handleRejectFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.rejectRequest(session.token, friendId),
    t('friends.requestRejected'),
  )
}

function handleCancelFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.cancelRequest(session.token, friendId),
    t('friends.requestCanceled'),
  )
}

function handleRemoveFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.removeFriend(session.token, friendId),
    t('friends.friendRemoved'),
  )
}

function handleBlockFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.blockUser(session.token, friendId),
    t('friends.userBlocked'),
  )
}

function handleUnblockFriend(friendId: number) {
  void runRelationshipMutation(
    () => dms.unblockUser(session.token, friendId),
    t('friends.userUnblocked'),
  )
}

function openAddServer(mode: 'create' | 'join' = 'create') {
  workspaceError.value = null
  clearWorkspaceNotice()
  addServerMode.value = mode
  showAddServer.value = true
}

function openCreateGuild() {
  openAddServer('create')
}

function closeAddServer() {
  showAddServer.value = false
}

function openDiscovery() {
  workspaceError.value = null
  clearWorkspaceNotice()
  showAddServer.value = false
  showDiscovery.value = true
}

function closeDiscovery() {
  showDiscovery.value = false
}

async function handleCreateGuild(name: string) {
  const trimmedName = name.trim()
  if (!trimmedName) return
  workspaceError.value = null
  isCreatingGuild.value = true
  try {
    await guilds.createGuild(session.token, trimmedName)
    closeAddServer()
    closeDiscovery()
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.guildCreateFailed')
  } finally {
    isCreatingGuild.value = false
  }
}

function handleCreateChannel(name: string, type: 0 | 1 = 0) {
  workspaceError.value = null
  clearWorkspaceNotice()
  void guilds.createChannel(session.token, name, type).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.channelCreateFailed')
  })
}

function handleSelectChannel(channelId: number) {
  clearWorkspaceNotice()
  activeHeaderPanel.value = null
  const channel = activeGuild.value?.channels.find((item) => item.id === channelId)
  if (channel?.type === 1) {
    handleOpenVoiceChannel(channelId)
    return
  }
  guilds.selectChannel(channelId)
}

function handleOpenVoiceChannel(channelId: number) {
  clearWorkspaceNotice()
  activeHeaderPanel.value = null
  navigation.openVoiceChannel()
  void handleJoinVoiceChannel(channelId)
}

function showHeaderPlaceholder(label: string) {
  setWorkspaceNotice(t('app.notice.localControl', { label }))
}

function toggleHeaderPanel(panel: 'threads' | 'notifications' | 'pins' | 'search') {
  workspaceError.value = null
  clearWorkspaceNotice()
  activeHeaderPanel.value = activeHeaderPanel.value === panel ? null : panel
}

function showDemoNotice(label: string) {
  setWorkspaceNotice(t('app.notice.demoDisabled', { label }))
}

async function copyToClipboard(value: string, successMessage: string, failureMessage: string) {
  workspaceError.value = null
  try {
    await writeClipboardText(value)
    setWorkspaceNotice(successMessage, 'success')
    return true
  } catch {
    setWorkspaceNotice(failureMessage, 'warning')
    return false
  }
}

function handleChannelSettings() {
  showHeaderPlaceholder(t('channel.aria.settings'))
}

function handleSendMessage(content: string) {
  workspaceError.value = null
  void guilds.sendMessage(session.token, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.messageSendFailed')
  })
}

function handleSendDmMessage(content: string) {
  if (!selectedDm.value) return
  workspaceError.value = null
  void dms.sendDmMessage(session.token, selectedDm.value.id, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.dmSendFailed')
  })
}

function handleDeleteDmMessage(messageId: number) {
  if (!selectedDm.value) return
  workspaceError.value = null
  void dms.deleteDmMessage(session.token, selectedDm.value.id, messageId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.messageDeleteFailed')
  })
}

function handleEditMessage(messageId: number, content: string) {
  workspaceError.value = null
  void guilds.editMessage(session.token, messageId, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.messageEditFailed')
  })
}

function handleDeleteMessage(messageId: number) {
  workspaceError.value = null
  void guilds.deleteMessage(session.token, messageId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.messageDeleteFailed')
  })
}

function handleCreateRole(name: string, permissions: number) {
  workspaceError.value = null
  void guilds.createRole(session.token, name, permissions).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.roleCreateFailed')
  })
}

function handleAssignRole(memberId: number, roleId: number) {
  workspaceError.value = null
  void guilds.assignRole(session.token, memberId, roleId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.roleAssignFailed')
  })
}

function handleRemoveRole(memberId: number, roleId: number) {
  workspaceError.value = null
  void guilds.removeRole(session.token, memberId, roleId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.roleRemoveFailed')
  })
}

function handleRefreshMembers() {
  workspaceError.value = null
  void guilds.refreshActiveGuild(session.token).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.memberRefreshFailed')
  })
}

function handleRemoveMember(memberId: number) {
  workspaceError.value = null
  void guilds.removeMember(session.token, memberId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.memberRemoveFailed')
  })
}

function cycleUserPresence() {
  const statuses: UserPresenceStatus[] = ['online', 'idle', 'dnd', 'offline']
  const currentIndex = statuses.indexOf(userPresenceStatus.value)
  const nextStatus = statuses[(currentIndex + 1) % statuses.length]
  userPresenceStatus.value = nextStatus
  updatePresence({ status: nextStatus, activity: null })
}

function handleOpenUserSettings(panel: 'account' | 'voice' = 'account') {
  workspaceError.value = null
  clearWorkspaceNotice()
  settingsInitialPanel.value = panel
  navigation.openSettings()
}

function handleOpenVoiceSettings() {
  handleOpenUserSettings('voice')
}

function openJoinGuild() {
  workspaceError.value = null
  openAddServer('join')
}

async function handleJoinGuild(code: string) {
  const trimmedCode = code.trim()
  if (!trimmedCode) return
  workspaceError.value = null
  isInviteWorking.value = true
  try {
    await guilds.joinInvite(session.token, trimmedCode)
    closeAddServer()
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.inviteJoinFailed')
  } finally {
    isInviteWorking.value = false
  }
}

async function handleCreateInvite() {
  workspaceError.value = null
  if (!guilds.canCreateInvite) {
    workspaceError.value = t('app.error.invitePermission')
    return
  }
  isInviteWorking.value = true
  try {
    const invite = await guilds.createInvite(session.token)
    openInvite(invite?.code ?? null)
  } catch (error) {
    workspaceError.value = formatInviteError(error)
  } finally {
    isInviteWorking.value = false
  }
}

function formatInviteError(error: unknown) {
  if (error instanceof Error && error.message.includes('create invite permission required')) {
    return t('app.error.invitePermission')
  }
  return error instanceof Error ? error.message : t('app.error.inviteCreateFailed')
}

async function copyInviteCode() {
  if (!inviteCode.value) return
  setInviteCodeCopied(await copyToClipboard(
    inviteCode.value,
    t('app.notice.inviteCopySuccess'),
    t('app.notice.copyFailed'),
  ))
}

async function handleSendInviteToFriend(friendId: number) {
  if (!inviteCode.value) return
  workspaceError.value = null
  setInviteFriendState(friendId, 'sending')
  try {
    const dm = await dms.createDm(session.token, [friendId])
    if (!dm) throw new Error(t('app.error.dmCreateFailed'))
    await dms.sendDmMessage(session.token, dm.id, t('invite.dmMessage', { code: inviteCode.value }))
    setInviteFriendState(friendId, 'sent')
    setWorkspaceNotice(t('invite.dmSent'), 'success')
  } catch (error) {
    setInviteFriendState(friendId, 'error')
    workspaceError.value = error instanceof Error ? error.message : t('app.error.dmSendFailed')
  }
}
</script>

<template>
  <div v-if="isBooting" class="boot-screen" role="status">{{ t('app.boot.loading') }}</div>

  <AuthPanel
    v-else-if="!session.token"
    :error="authError"
    :loading="isAuthenticating"
    @login="handleLogin"
    @register="handleRegister"
    @demo="handleDemo"
  />

  <main
    v-else
    class="app-shell"
    :class="{
      'settings-mode': navigation.destination === 'settings',
      'voice-connected': guilds.voiceConnected,
      'voice-error': Boolean(voiceErrorMessage),
      'friends-mode': navigation.destination === 'friends',
    }"
    :data-gateway-status="gatewayStatus"
    :data-local-microphone-muted="localMicrophoneTracksMuted"
    :aria-label="t('app.aria.workspace')"
    @mousedown="handleWorkspacePointerDown"
    @contextmenu.prevent="openGlobalContextMenu"
  >
    <ServerRail
      v-if="navigation.destination !== 'settings'"
      :guilds="guilds.guilds"
      :active-guild-id="guilds.activeGuildId"
      :home-active="isPrivateDestination"
      :home-unread-count="dms.unreadCount"
      :guild-meta="serverRailMeta"
      @home="handleOpenFriends"
      @select="handleSelectGuild"
      @create="openCreateGuild"
      @discover="openDiscovery"
    />

    <PrivateChannelSidebar
      v-if="isPrivateDestination"
      :dms="dms.dms"
      :active-dm-id="navigation.activeDmId"
      :active-destination="navigation.destination"
      @open-friends="handleOpenFriends"
      @open-dm="handleOpenDm"
      @create-dm="showCreateDmDialog = true"
      @close-dm="handleCloseDm"
      @demo-notice="showDemoNotice"
    />

    <ChannelSidebar
      v-else-if="navigation.destination !== 'settings' && activeGuild"
      :guild="activeGuild"
      :active-channel-id="guilds.activeChannelId"
      :voice-states="guilds.voiceStates"
      :connected-voice-channel-id="activeGuildConnectedVoiceChannelId"
      :current-user-id="session.user?.id ?? null"
      :local-speaking="voiceRtc.localSpeaking.value"
      :muted="voiceRtc.isMuted.value"
      :deafened="isDeafened"
      :can-create-invite="guilds.canCreateInvite"
      @select="handleSelectChannel"
      @create-channel="handleCreateChannel"
      @create-invite="handleCreateInvite"
      @channel-settings="handleChannelSettings"
      @join-voice="handleOpenVoiceChannel"
      @leave-voice="handleLeaveVoiceChannel"
      @demo-notice="showDemoNotice"
    />

    <section class="workspace">
      <header v-if="showWorkspaceTopbar" class="topbar">
        <div class="channel-title">
          <Settings v-if="navigation.destination === 'settings'" :size="19" aria-hidden="true" />
          <Radio v-else-if="isServerDestination && activeChannel?.type === 1" :size="19" aria-hidden="true" />
          <Hash v-else :size="19" aria-hidden="true" />
          <span class="channel-title-copy">
            <span>{{ workspaceTitle }}</span>
            <small>{{ workspaceSubtitle }}</small>
          </span>
        </div>
        <button
          v-if="navigation.destination === 'settings'"
          class="topbar-icon-button settings-topbar-close"
          type="button"
          :title="t('settings.close')"
          :aria-label="t('settings.close')"
          @click="navigation.closeSettings"
        >
          <X :size="18" aria-hidden="true" />
        </button>
        <div v-if="isServerDestination" class="channel-header-tools" :aria-label="t('app.header.channelTools')">
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.notifications')"
            :aria-label="t('app.header.notifications')"
            :aria-expanded="activeHeaderPanel === 'notifications'"
            @click="toggleHeaderPanel('notifications')"
          >
            <Bell :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.pins')"
            :aria-label="t('app.header.pins')"
            :aria-expanded="activeHeaderPanel === 'pins'"
            @click="toggleHeaderPanel('pins')"
          >
            <Pin :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.memberList')"
            :aria-label="t('app.header.memberList')"
            :class="{ active: showMemberList }"
            @click="showMemberList = !showMemberList"
          >
            <Users :size="17" aria-hidden="true" />
          </button>
          <label class="topbar-search">
            <Search :size="15" aria-hidden="true" />
            <input
              v-model="channelSearchQuery"
              type="search"
              :placeholder="t('app.header.search')"
              :aria-label="t('app.header.searchMessages')"
              @focus="activeHeaderPanel = 'search'"
              @input="activeHeaderPanel = 'search'"
            />
          </label>
        </div>
        <div v-if="isServerDestination" class="topbar-actions">
          <button
            v-if="isServerDestination && guilds.canCreateInvite"
            class="topbar-icon-button"
            type="button"
            :aria-label="t('app.header.createInvite')"
            :disabled="!activeGuild || isInviteWorking"
            @click="handleCreateInvite"
          >
            <Link :size="17" aria-hidden="true" />
          </button>
        </div>
      </header>

      <section v-if="isServerDestination && activeHeaderPanel" class="channel-header-panel" role="dialog">
        <div class="channel-header-panel-title">
          <strong>
            {{
              activeHeaderPanel === 'threads'
                ? t('headerPanel.threads.title')
                : activeHeaderPanel === 'notifications'
                  ? t('headerPanel.notifications.title')
                  : activeHeaderPanel === 'pins'
                    ? t('headerPanel.pins.title')
                    : t('headerPanel.search.title')
            }}
          </strong>
          <button type="button" @click="activeHeaderPanel = null">{{ t('common.close') }}</button>
        </div>

        <div v-if="activeHeaderPanel === 'notifications'" class="header-panel-options">
          <label>
            <input v-model="notificationMode" type="radio" value="all" />
            <span>{{ t('headerPanel.notifications.all') }}</span>
          </label>
          <label>
            <input v-model="notificationMode" type="radio" value="mentions" />
            <span>{{ t('headerPanel.notifications.mentions') }}</span>
          </label>
          <label>
            <input v-model="notificationMode" type="radio" value="none" />
            <span>{{ t('headerPanel.notifications.none') }}</span>
          </label>
          <small>{{ t('headerPanel.notifications.saved') }}</small>
        </div>

        <div v-else-if="activeHeaderPanel === 'search'" class="header-panel-search">
          <input
            v-model="channelSearchQuery"
            type="search"
            :placeholder="t('headerPanel.search.placeholder')"
            autofocus
          />
          <div v-if="!channelSearchQuery.trim()" class="header-panel-empty">
            {{ t('headerPanel.search.empty') }}
          </div>
          <div v-else-if="!channelSearchResults.length" class="header-panel-empty">
            {{ t('headerPanel.search.noResults') }}
          </div>
          <button
            v-for="message in channelSearchResults.slice(0, 8)"
            :key="message.id"
            type="button"
            class="header-panel-result"
          >
            <strong>{{ message.author_name }}</strong>
            <span>{{ message.content }}</span>
          </button>
        </div>

        <div v-else class="header-panel-empty">
          {{
            activeHeaderPanel === 'threads'
              ? t('headerPanel.threads.empty')
              : t('headerPanel.pins.empty')
          }}
        </div>
      </section>

      <div class="workspace-alerts">
        <div v-if="authError || workspaceError || guilds.error || dms.error" class="app-error" role="alert">
          {{ authError ?? workspaceError ?? guilds.error ?? dms.error }}
        </div>
        <div v-if="pendingVoiceRejoinSummary" class="voice-rejoin-notice" role="status">
          <div>
            <strong>{{ t('voice.rejoinTitle') }}</strong>
            <span>
              {{
                t('voice.rejoinDescription', {
                  guild: pendingVoiceRejoinSummary.guild.name,
                  channel: pendingVoiceRejoinSummary.channel.name,
                })
              }}
            </span>
          </div>
          <div class="voice-rejoin-actions">
            <button type="button" class="primary" @click="handleConfirmVoiceRejoin">
              <Radio :size="15" aria-hidden="true" />
              <span>{{ t('voice.rejoinAction') }}</span>
            </button>
            <button type="button" class="danger" :aria-label="t('voice.rejoinDismiss')" @click="dismissVoiceRejoin">
              <PhoneOff :size="14" aria-hidden="true" />
              <span>{{ t('voice.leaveSelected') }}</span>
            </button>
          </div>
        </div>
        <div v-if="incomingDmCall" class="dm-incoming-call-notice" role="alert">
          <span class="dm-incoming-call-icon" aria-hidden="true">
            <Phone :size="18" />
          </span>
          <div>
            <strong>{{ t('friends.incomingDmCallTitle', { target: incomingDmCall.callerName }) }}</strong>
            <span>{{ t('friends.incomingDmCallDescription') }}</span>
          </div>
          <div class="dm-incoming-call-actions">
            <button type="button" class="primary" @click="handleAcceptIncomingDmCall">
              <Phone :size="15" aria-hidden="true" />
              <span>{{ t('friends.acceptCall') }}</span>
            </button>
            <button type="button" class="danger" @click="handleDismissIncomingDmCall">
              <PhoneOff :size="15" aria-hidden="true" />
              <span>{{ t('friends.declineCall') }}</span>
            </button>
          </div>
        </div>
        <div v-if="workspaceNotice" class="app-notice" :class="workspaceNoticeTone" role="status">
          <span>{{ workspaceNotice }}</span>
          <button type="button" :aria-label="t('common.close')" @click="clearWorkspaceNotice">
            <X :size="14" aria-hidden="true" />
          </button>
        </div>
      </div>

      <div v-if="guilds.isLoading || dms.isLoading" class="workspace-loading" role="status">
        {{ t('app.workspace.loading') }}
      </div>

      <SettingsView
        v-if="navigation.destination === 'settings'"
        :current-user="session.user"
        :initial-panel="settingsInitialPanel"
        :user-status="userPresenceStatus"
        :muted="voiceRtc.isMuted.value"
        :deafened="isDeafened"
        :input-level="voiceRtc.inputLevel.value"
        :turn-configured="voiceTurnConfigured"
        :voice-connected="guilds.voiceConnected"
        :constraint-support="voiceRtc.constraintSupport.value"
        :voice-device-settings="voiceRtc.voiceDeviceSettings.value"
        :voice-devices="voiceRtc.voiceDevices.value"
        @close="navigation.closeSettings"
        @logout="handleLogout"
        @update-voice-device-settings="voiceRtc.updateVoiceDeviceSettings"
        @refresh-voice-devices="voiceRtc.refreshVoiceDevices"
      />

      <FriendsHome
        v-else-if="navigation.destination === 'friends'"
        :friends="dms.relationships"
        :disabled="dms.isMutating"
        :action-notice="workspaceNotice"
        :action-error="workspaceError ?? dms.error"
        :pending-request-focus-key="pendingRequestFocusKey"
        :reset-tab-key="friendsHomeResetKey"
        @add-friend="handleAddFriend"
        @accept-friend="handleAcceptFriend"
        @reject-friend="handleRejectFriend"
        @cancel-friend="handleCancelFriend"
        @remove-friend="handleRemoveFriend"
        @block-friend="handleBlockFriend"
        @unblock-friend="handleUnblockFriend"
        @message-friend="handleMessageFriend"
        @view-profile="handleViewProfile"
        @call-friend="handleStartFriendCall"
        @toggle-mute-friend="handleToggleFriendMute"
      />

      <DirectMessageView
        v-else-if="navigation.destination === 'dm'"
        :dm="selectedDm"
        :current-user="session.user"
        :disabled="dms.isMutating"
        :muted="selectedDmMuted"
        :voice-muted="voiceRtc.isMuted.value"
        :deafened="isDeafened"
        :call-active="connectedDmId === selectedDm?.id"
        :call-joinable="selectedDmCallJoinable"
        :voice-device-settings="voiceRtc.voiceDeviceSettings.value"
        :voice-devices="voiceRtc.voiceDevices.value"
        @view-profile="handleViewSelectedDmProfile"
        @start-call="handleStartSelectedDmCall"
        @leave-call="disconnectVoice"
        @toggle-mute="handleToggleSelectedDmMute"
        @toggle-voice-mute="handleToggleMute"
        @toggle-deafen="handleToggleDeafen"
        @open-voice-settings="handleOpenVoiceSettings"
        @refresh-voice-devices="voiceRtc.refreshVoiceDevices"
        @update-voice-device-settings="voiceRtc.updateVoiceDeviceSettings"
        @send="handleSendDmMessage"
        @delete-message="handleDeleteDmMessage"
      />

      <section
        v-else-if="activeGuild && selectedVoiceChannel"
        class="voice-workspace"
        :aria-label="t('voice.workspaceAria')"
      >
        <header class="voice-workspace-header">
          <div>
            <span class="voice-workspace-icon"><Radio :size="22" aria-hidden="true" /></span>
            <div>
              <h2>{{ selectedVoiceChannel.name }}</h2>
              <p class="voice-workspace-status">{{ activeGuild.name }} / {{ voiceWorkspaceStatus }}</p>
            </div>
          </div>
          <div class="voice-workspace-actions">
            <button
              v-if="!selectedVoiceConnected"
              type="button"
              class="primary"
              :aria-label="t('voice.joinSelected')"
              @click="handleJoinVoiceChannel(selectedVoiceChannel.id)"
            >
              <Mic :size="17" aria-hidden="true" />
              <span>{{ t('voice.joinSelected') }}</span>
            </button>
            <button
              v-if="selectedVoiceConnected"
              type="button"
              class="danger"
              :aria-label="t('voice.leaveSelected')"
              @click="handleLeaveVoiceChannel(selectedVoiceChannel.id)"
            >
              <PhoneOff :size="17" aria-hidden="true" />
              <span>{{ t('voice.leaveSelected') }}</span>
            </button>
            <button
              type="button"
              class="screen"
              :class="{ active: voiceRtc.isScreenSharing.value }"
              :aria-label="voiceRtc.isScreenSharing.value ? t('voice.stopScreenShare') : t('voice.screenShare')"
              :aria-pressed="voiceRtc.isScreenSharing.value"
              :disabled="!selectedVoiceConnected"
              @click="handleToggleScreenShare"
            >
              <ScreenShareOff v-if="voiceRtc.isScreenSharing.value" :size="17" aria-hidden="true" />
              <ScreenShare v-else :size="17" aria-hidden="true" />
              <span>{{ voiceRtc.isScreenSharing.value ? t('voice.stopScreenShare') : t('voice.screenShare') }}</span>
            </button>
          </div>
        </header>

        <div
          v-if="voiceRtc.screenStream.value || remoteScreenStreams.length"
          class="screen-share-stage"
          aria-label="Screen shares"
        >
          <VoiceVideoSink
            v-if="voiceRtc.screenStream.value"
            class="local-screen-share-tile"
            :stream="voiceRtc.screenStream.value"
            :label="t('voice.screenPreview')"
            :subtitle="session.user?.username ?? t('common.demoUser')"
            :user-id="session.user?.id"
            state="connected"
          />
          <VoiceVideoSink
            v-for="remote in remoteScreenStreams"
            :key="`${remote.channelId}:${remote.userId}`"
            :stream="remote.stream"
            :label="t('voice.remoteScreenLabel', { user: remote.username ?? `User ${remote.userId}` })"
            :subtitle="remote.connectionState === 'connected' ? t('common.status.connected') : remote.connectionState"
            :state="remote.connectionState"
            :user-id="remote.userId"
          />
        </div>

        <div class="voice-workspace-grid">
          <article
            class="voice-tile local"
            :class="{ connected: selectedVoiceConnected, speaking: voiceRtc.localSpeaking.value }"
          >
            <span class="voice-tile-avatar">{{ session.user?.username.slice(0, 2).toUpperCase() ?? 'YA' }}</span>
            <div>
              <strong>{{ session.user?.username ?? t('common.demoUser') }}</strong>
              <span>{{ selectedVoiceConnected ? voiceWorkspaceStatus : t('voice.localPreview') }}</span>
            </div>
            <small v-if="voiceRtc.isScreenSharing.value">{{ t('voice.screenLive') }}</small>
          </article>

          <article v-if="!visibleSelectedVoicePeers.length && !remoteScreenStreams.length" class="voice-tile empty">
            <UserRound :size="34" aria-hidden="true" />
            <div>
              <strong>{{ t('voice.noRemoteParticipants') }}</strong>
              <span>{{ t('voice.inviteHint') }}</span>
            </div>
          </article>

          <article
            v-for="participant in visibleSelectedVoicePeers"
            :key="participant.user_id"
            class="voice-tile remote"
            :class="{ speaking: remoteVoiceStreamByUserId.get(participant.user_id)?.speaking }"
            :data-user-id="participant.user_id"
          >
            <span class="voice-tile-avatar remote">
              {{ (participant.username ?? `U${participant.user_id}`).slice(0, 2).toUpperCase() }}
            </span>
            <div>
              <strong>{{ participant.username ?? `User ${participant.user_id}` }}</strong>
              <span>
                {{
                  participant.self_mute
                    ? t('common.status.muted')
                    : remoteVoiceStreamByUserId.get(participant.user_id)?.speaking
                      ? t('voice.speaking')
                      : t('common.status.connected')
                }}
              </span>
            </div>
          </article>
        </div>

        <aside v-if="workspaceError" class="voice-workspace-error" role="status">
          {{ workspaceError }}
        </aside>
      </section>

      <div v-else-if="activeGuild" class="content-grid" :class="{ 'members-hidden': !showMemberList }">
        <ChatView
          :channel="activeChannel"
          :messages="activeMessages"
          :current-user="session.user"
          :can-manage-messages="guilds.canManageMessages"
          @send="handleSendMessage"
          @edit="handleEditMessage"
          @delete="handleDeleteMessage"
        />
        <MemberList
          v-if="activeGuild && showMemberList"
          :members="activeGuild.members"
          :roles="activeGuild.roles"
          :can-manage-roles="guilds.canManageRoles"
          :owner-id="activeGuild.owner_id"
          :current-user-id="session.user?.id"
          :disabled="guilds.isMutating"
          @create-role="handleCreateRole"
          @assign-role="handleAssignRole"
          @remove-role="handleRemoveRole"
          @remove-member="handleRemoveMember"
          @refresh="handleRefreshMembers"
        />
      </div>

      <section v-else class="empty-workspace" :aria-label="t('app.empty.noServers')">
        <div>{{ t('app.empty.noServers') }}</div>
        <div class="empty-actions">
          <button type="button" @click="openCreateGuild">{{ t('app.empty.createServer') }}</button>
          <button type="button" @click="openJoinGuild">{{ t('app.empty.joinServer') }}</button>
        </div>
      </section>
    </section>

    <ServerAddDialog
      v-if="showAddServer"
      :initial-mode="addServerMode"
      :loading="isCreatingGuild || isInviteWorking || guilds.isMutating"
      @close="closeAddServer"
      @create="handleCreateGuild"
      @join="handleJoinGuild"
      @discover="openDiscovery"
    />

    <ServerDiscoveryDialog
      v-if="showDiscovery"
      @close="closeDiscovery"
      @create-server="handleCreateGuild"
    />

    <section
      v-if="showInvite"
      class="modal-layer"
      :aria-label="t('invite.title')"
      @click.self="closeInvite"
    >
      <div class="invite-dialog" role="dialog" :aria-label="t('invite.title')">
        <header class="invite-dialog-header">
          <div>
            <h2>{{ t('invite.title') }}</h2>
            <p>{{ activeGuild?.name }}</p>
          </div>
          <button type="button" :aria-label="t('common.close')" @click="closeInvite">
            <X :size="18" aria-hidden="true" />
          </button>
        </header>
        <label class="invite-search">
          <Search :size="16" aria-hidden="true" />
          <input v-model="inviteSearchQuery" :placeholder="t('invite.search')" autocomplete="off" autofocus />
        </label>
        <div class="invite-friend-list">
          <article v-for="friend in inviteFriends" :key="friend.id" class="invite-friend-row">
            <span class="friend-avatar">{{ friend.username.slice(0, 1).toUpperCase() }}</span>
            <span>
              <strong>{{ friend.username }}</strong>
              <small>{{ friend.activity ?? friend.handle }}</small>
            </span>
            <button
              type="button"
              :class="{ sent: inviteFriendState(friend.id) === 'sent', error: inviteFriendState(friend.id) === 'error' }"
              :disabled="isInviteWorking || dms.isMutating || inviteFriendState(friend.id) === 'sending'"
              @click="handleSendInviteToFriend(friend.id)"
            >
              {{
                inviteFriendState(friend.id) === 'sending'
                  ? t('invite.sending')
                  : inviteFriendState(friend.id) === 'sent'
                    ? t('invite.sent')
                    : inviteFriendState(friend.id) === 'error'
                      ? t('invite.retry')
                      : t('invite.send')
              }}
            </button>
          </article>
          <p v-if="!inviteFriends.length" class="invite-empty">{{ t('friends.empty') }}</p>
        </div>
        <div class="invite-output">
          <span>{{ t('invite.linkLabel') }}</span>
          <strong>{{ inviteCode }}</strong>
          <button type="button" @click="copyInviteCode">
            {{ inviteCodeCopied ? t('invite.copied') : t('invite.copy') }}
          </button>
        </div>
      </div>
    </section>

    <section
      v-if="pendingVoiceSwitchChannelId"
      class="modal-layer voice-switch-layer"
      :aria-label="t('voice.switchTitle')"
      @click.self="cancelVoiceSwitch"
    >
      <div class="voice-switch-dialog" role="dialog" :aria-label="t('voice.switchTitle')" aria-modal="true">
        <button type="button" class="voice-switch-close" :aria-label="t('common.close')" @click="cancelVoiceSwitch">
          <X :size="26" aria-hidden="true" />
        </button>
        <header>
          <h2>{{ t('voice.switchTitle') }}</h2>
          <p>{{ t('voice.switchDescription') }}</p>
        </header>
        <footer>
          <label class="voice-switch-checkbox">
            <input v-model="rememberVoiceSwitchChoice" type="checkbox" />
            <span>{{ t('voice.dontAskAgain') }}</span>
          </label>
          <div class="voice-switch-actions">
            <button type="button" class="secondary" @click="cancelVoiceSwitch">
              {{ t('common.cancel') }}
            </button>
            <button type="button" class="primary" @click="confirmVoiceSwitch">
              {{ t('common.confirm') }}
            </button>
          </div>
        </footer>
      </div>
    </section>

    <VoicePanel
      v-if="navigation.destination !== 'settings'"
      :channel="voicePanelChannel"
      :current-user="session.user"
      :user-status="userPresenceStatus"
      :connected="voiceConnected"
      :connected-guild-name="connectedDmId !== null ? t('app.status.directMessage') : guilds.connectedVoiceGuild?.name ?? null"
      :connected-elsewhere="voiceConnectedElsewhere"
      :signaling-ready="gatewayStatus === 'connected'"
      :local-speaking="voiceRtc.localSpeaking.value"
      :muted="voiceRtc.isMuted.value"
      :deafened="isDeafened"
      :screen-sharing="voiceRtc.isScreenSharing.value"
      :quality-stats="voiceRtc.qualityStats.value"
      :turn-configured="voiceTurnConfigured"
      :error="voiceErrorMessage"
      :voice-device-settings="voiceRtc.voiceDeviceSettings.value"
      :voice-devices="voiceRtc.voiceDevices.value"
      @toggle="handleToggleVoice"
      @toggle-mute="handleToggleMute"
      @toggle-deafen="handleToggleDeafen"
      @toggle-screen="handleToggleScreenShare"
      @retry="handleRetryVoiceCapture"
      @leave="handleLeaveVoiceFromError"
      @cycle-status="cycleUserPresence"
      @open-user-settings="handleOpenUserSettings"
      @open-voice-settings="handleOpenVoiceSettings"
      @update-voice-device-settings="voiceRtc.updateVoiceDeviceSettings"
      @refresh-voice-devices="voiceRtc.refreshVoiceDevices"
    />
    <div class="voice-audio-sinks" aria-hidden="true">
      <VoiceAudioSink
        v-for="remote in activeRemoteVoiceStreams"
        :key="`${remote.channelId}:${remote.userId}`"
        :stream="remote.stream"
        :muted="isDeafened"
        :output-device-id="voiceRtc.voiceDeviceSettings.value.outputDeviceId"
        :volume="voiceRtc.voiceDeviceSettings.value.outputVolume"
      />
    </div>
    <div
      v-if="globalContextMenu"
      class="global-context-menu"
      :style="{ left: `${globalContextMenu.x}px`, top: `${globalContextMenu.y}px` }"
      role="menu"
      @mousedown.stop
      @click.stop
      @contextmenu.stop.prevent
    >
      <strong>{{ globalContextMenu.title }}</strong>
      <button
        v-for="item in globalContextMenu.items"
        :key="item.id"
        type="button"
        role="menuitem"
        :class="{ danger: item.danger }"
        @click="runGlobalContextAction(item.id)"
      >
        {{ item.label }}
      </button>
    </div>

    <CreateDmDialog
      :open="showCreateDmDialog"
      :friends="dms.relationships"
      :disabled="dms.isMutating"
      @close="showCreateDmDialog = false"
      @create="handleCreateDm"
    />

    <FriendProfileDialog
      :friend="profileFriend"
      :muted="Boolean(profileFriend && dms.dms.some((dm) => dm.recipient_ids.length === 1 && dm.recipient_ids[0] === profileFriend?.id && preferences.isDmMuted(dm.id)))"
      @close="profileFriendId = null"
      @message="handleMessageFriend"
      @call="handleStartFriendCall"
      @toggle-mute="handleToggleFriendMute"
    />
  </main>
</template>
