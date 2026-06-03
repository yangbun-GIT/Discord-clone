<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  Bell,
  CircleHelp,
  Hash,
  Inbox,
  Link,
  List,
  LogIn,
  LogOut,
  Pin,
  Radio,
  Search,
  Settings,
  Users,
  Wifi,
  WifiOff,
} from 'lucide-vue-next'

import { apiGet } from './services/api'
import AuthPanel from './components/AuthPanel.vue'
import ChannelSidebar from './components/ChannelSidebar.vue'
import ChatView from './components/ChatView.vue'
import DirectMessageView from './components/DirectMessageView.vue'
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
import { useGateway } from './composables/useGateway'
import { useVoiceRtc } from './composables/useVoiceRtc'
import { useI18n } from './i18n'
import { useDmStore } from './stores/dms'
import { useGuildStore } from './stores/guilds'
import { useNavigationStore } from './stores/navigation'
import { usePreferencesStore } from './stores/preferences'
import { useSessionStore } from './stores/session'
import { useStoreStore } from './stores/store'
import type { ServerRailGuildMeta, UserPresenceStatus, VoiceConfig, VoiceIceServer } from './types'

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
  status: gatewayStatus,
  statusLabel,
} = useGateway()
const voiceRtc = useVoiceRtc()

const activeGuild = computed(() => guilds.activeGuild)
const activeChannel = computed(() => guilds.activeChannel)
const activeMessages = computed(() => guilds.activeMessages)
const remoteScreenStreams = computed(() =>
  voiceRtc.remoteStreams.value.filter((remote) => remote.sharingScreen),
)
const workspaceTitle = computed(() => {
  if (navigation.destination === 'friends') return t('app.status.friends')
  if (navigation.destination === 'dm') {
    return dms.getDm(navigation.activeDmId)?.display_name ?? t('app.status.directMessage')
  }
  if (navigation.destination === 'settings') return t('app.status.userSettings')
  if (!activeGuild.value) return t('app.status.noServers')
  return activeChannel.value?.name ?? t('app.status.loading')
})
const workspaceSubtitle = computed(() => {
  if (navigation.destination === 'friends') return t('app.location.privateHome')
  if (navigation.destination === 'dm') return t('app.location.directMessage')
  if (navigation.destination === 'settings') return t('app.location.settings')
  if (!activeGuild.value) return t('app.location.noServer')
  const channelKind = activeChannel.value?.type === 1 ? t('app.location.voiceChannel') : t('app.location.textChannel')
  return `${activeGuild.value.name} / ${channelKind}`
})
const voiceLocationSummary = computed(() => {
  if (!guilds.voiceConnected || !guilds.voiceChannel || !activeGuild.value) return null
  const state = isDeafened.value
    ? t('common.status.deafened')
    : voiceRtc.isMuted.value
      ? t('common.status.muted')
      : voiceRtc.localSpeaking.value
        ? t('voice.speaking')
        : t('common.status.connected')
  return `${activeGuild.value.name} / ${guilds.voiceChannel.name} · ${state}`
})
const isPrivateDestination = computed(() =>
  navigation.destination === 'friends' || navigation.destination === 'dm',
)
const isServerDestination = computed(() =>
  navigation.destination === 'server_channel' || navigation.destination === 'voice_channel',
)
const selectedDm = computed(() => dms.getDm(navigation.activeDmId))
const isBooting = ref(true)
const authError = ref<string | null>(null)
const workspaceError = ref<string | null>(null)
const workspaceNotice = ref<string | null>(null)
const isAuthenticating = ref(false)
const isCreatingGuild = ref(false)
const isInviteWorking = ref(false)
const activeHeaderPanel = ref<'threads' | 'notifications' | 'pins' | 'search' | null>(null)
const notificationMode = ref<'all' | 'mentions' | 'none'>('all')
const channelSearchQuery = ref('')
const showAddServer = ref(false)
const addServerMode = ref<'create' | 'join'>('create')
const showDiscovery = ref(false)
const showInvite = ref(false)
const showMemberList = ref(true)
const inviteCode = ref<string | null>(null)
const voiceIceServers = ref<VoiceIceServer[]>([{ urls: 'stun:stun.l.google.com:19302' }])
const voiceTurnConfigured = ref(false)
const userPresenceStatus = ref<UserPresenceStatus>('online')
const isDeafened = ref(false)
const connectedVoiceChannelId = computed(() => (guilds.voiceConnected ? guilds.voiceChannel?.id ?? null : null))
const serverRailMeta = computed<Record<number, ServerRailGuildMeta>>(() => {
  const entries = guilds.guilds.map((guild, index) => {
    const unreadCount = activeGuild.value?.id === guild.id ? 0 : Math.min(guild.messages.length, 9)
    return [
      guild.id,
      {
        unread_count: unreadCount,
        mention_count: index === 0 && !isPrivateDestination.value ? 0 : Number(index === 0 && unreadCount > 0),
        muted: index % 3 === 2,
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

async function openWorkspace() {
  if (!session.token) return
  await Promise.all([
    guilds.loadGuilds(session.token),
    dms.loadPrivateWorkspace(session.token),
    loadVoiceConfig(),
  ])
  navigation.openFriends()
  connectGateway(session.token, {
    onDispatch: (event, data) => {
      guilds.handleGatewayDispatch(event, data)
      dms.handleGatewayDispatch(event, data)
    },
  })
}

async function loadVoiceConfig() {
  const config = await apiGet<VoiceConfig>('/api/meta/voice')
  voiceIceServers.value = config.ice_servers
  voiceTurnConfigured.value = config.turn_configured
}

onMounted(async () => {
  preferences.restorePreferences()
  await session.restoreSession()
  if (session.token) {
    await openWorkspace()
  }
  isBooting.value = false
})

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
  voiceRtc.disconnect()
  disconnectGateway()
  authError.value = null
  workspaceError.value = null
  workspaceNotice.value = null
  session.logout()
  navigation.resetNavigation()
  guilds.resetGuilds()
  dms.resetDms()
  store.resetStoreState()
  userPresenceStatus.value = 'online'
  isDeafened.value = false
}

function handleSelectGuild(guildId: number) {
  workspaceNotice.value = null
  activeHeaderPanel.value = null
  navigation.openServerChannel()
  guilds.selectGuild(guildId)
}

function handleOpenFriends() {
  workspaceNotice.value = null
  activeHeaderPanel.value = null
  navigation.openFriends()
}

function handleOpenDm(dmId: number) {
  workspaceNotice.value = null
  activeHeaderPanel.value = null
  navigation.openDm(dmId)
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

function openAddServer(mode: 'create' | 'join' = 'create') {
  workspaceError.value = null
  workspaceNotice.value = null
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
  workspaceNotice.value = null
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
  workspaceNotice.value = null
  void guilds.createChannel(session.token, name, type).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.channelCreateFailed')
  })
}

function showHeaderPlaceholder(label: string) {
  workspaceError.value = null
  workspaceNotice.value = t('app.notice.localControl', { label })
}

function toggleHeaderPanel(panel: 'threads' | 'notifications' | 'pins' | 'search') {
  workspaceError.value = null
  workspaceNotice.value = null
  activeHeaderPanel.value = activeHeaderPanel.value === panel ? null : panel
}

function showDemoNotice(label: string) {
  workspaceError.value = null
  workspaceNotice.value = t('app.notice.demoDisabled', { label })
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

function disconnectVoice() {
  if (!activeGuild.value) return
  updateVoiceState({
    guild_id: activeGuild.value.id,
    channel_id: null,
    self_mute: false,
    self_deaf: false,
  })
  voiceRtc.disconnect()
  guilds.setVoiceConnected(false)
}

function voiceParticipantsForChannel(channelId: number) {
  return guilds.voiceStates.filter((state) => state.channel_id === channelId)
}

async function connectVoiceToChannel(channelId: number) {
  if (!activeGuild.value || !session.user) return
  const targetChannel = activeGuild.value.channels.find((channel) => channel.id === channelId && channel.type === 1)
  if (!targetChannel) return

  try {
    await voiceRtc.connect({
      channelId: targetChannel.id,
      currentUserId: session.user.id,
      participants: voiceParticipantsForChannel(targetChannel.id),
      iceServers: voiceIceServers.value,
      sendSignal: sendVoiceSignal,
    })
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.voiceConnectFailed')
    return
  }

  guilds.setVoiceConnected(true)
  updateVoiceState({
    guild_id: activeGuild.value.id,
    channel_id: targetChannel.id,
    self_mute: voiceRtc.isMuted.value,
    self_deaf: isDeafened.value,
  })
}

async function handleToggleVoice() {
  if (!activeGuild.value || !guilds.voiceChannel || !session.user) return
  if (guilds.voiceConnected) {
    disconnectVoice()
    return
  }

  await connectVoiceToChannel(guilds.voiceChannel.id)
}

async function handleJoinVoiceChannel(channelId: number) {
  workspaceError.value = null
  guilds.selectChannel(channelId)
  if (connectedVoiceChannelId.value === channelId) return
  if (guilds.voiceConnected) {
    disconnectVoice()
  }
  await connectVoiceToChannel(channelId)
}

function handleLeaveVoiceChannel(channelId: number) {
  workspaceError.value = null
  if (connectedVoiceChannelId.value !== channelId) return
  disconnectVoice()
}

function cycleUserPresence() {
  const statuses: UserPresenceStatus[] = ['online', 'idle', 'dnd', 'offline']
  const currentIndex = statuses.indexOf(userPresenceStatus.value)
  userPresenceStatus.value = statuses[(currentIndex + 1) % statuses.length]
}

function handleToggleDeafen() {
  isDeafened.value = !isDeafened.value
  if (!activeGuild.value || !guilds.voiceConnected || !guilds.voiceChannel) return
  updateVoiceState({
    guild_id: activeGuild.value.id,
    channel_id: guilds.voiceChannel.id,
    self_mute: voiceRtc.isMuted.value,
    self_deaf: isDeafened.value,
  })
}

function handleOpenUserSettings() {
  workspaceError.value = null
  workspaceNotice.value = null
  navigation.openSettings()
}

function handleToggleMute() {
  voiceRtc.toggleMute()
  if (!activeGuild.value || !guilds.voiceConnected || !guilds.voiceChannel) return
  updateVoiceState({
    guild_id: activeGuild.value.id,
    channel_id: guilds.voiceChannel.id,
    self_mute: voiceRtc.isMuted.value,
    self_deaf: isDeafened.value,
  })
}

function handleToggleScreenShare() {
  workspaceError.value = null
  void voiceRtc.toggleScreenShare().catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.screenShareFailed')
  })
}

watch(
  () => guilds.activeVoiceStates.map((state) => `${state.user_id}:${state.channel_id}`).join('|'),
  () => {
    if (!voiceRtc.isCapturing.value || !session.user) return
    void voiceRtc.syncParticipants(guilds.activeVoiceStates).catch((error) => {
      workspaceError.value = error instanceof Error ? error.message : t('app.error.voicePeerSyncFailed')
    })
  },
)

watch(
  () => guilds.lastVoiceSignal,
  (signal) => {
    if (!signal) return
    void voiceRtc.handleSignal(signal).catch((error) => {
      workspaceError.value = error instanceof Error ? error.message : t('app.error.voiceSignalFailed')
    })
  },
)

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

function closeInvite() {
  showInvite.value = false
  inviteCode.value = null
}

async function handleCreateInvite() {
  workspaceError.value = null
  isInviteWorking.value = true
  try {
    const invite = await guilds.createInvite(session.token)
    inviteCode.value = invite?.code ?? null
    showInvite.value = true
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : t('app.error.inviteCreateFailed')
  } finally {
    isInviteWorking.value = false
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
    :class="{ 'settings-mode': navigation.destination === 'settings' }"
    :aria-label="t('app.aria.workspace')"
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
      @create-dm="handleOpenFriends"
      @demo-notice="showDemoNotice"
    />

    <ChannelSidebar
      v-else-if="navigation.destination !== 'settings' && activeGuild"
      :guild="activeGuild"
      :active-channel-id="guilds.activeChannelId"
      :voice-states="guilds.voiceStates"
      :connected-voice-channel-id="connectedVoiceChannelId"
      :current-user-id="session.user?.id ?? null"
      :local-speaking="voiceRtc.localSpeaking.value"
      :muted="voiceRtc.isMuted.value"
      :deafened="isDeafened"
      @select="guilds.selectChannel"
      @create-channel="handleCreateChannel"
      @create-invite="handleCreateInvite"
      @channel-settings="handleChannelSettings"
      @join-voice="handleJoinVoiceChannel"
      @leave-voice="handleLeaveVoiceChannel"
      @demo-notice="showDemoNotice"
    />

    <section class="workspace">
      <header class="topbar">
        <div class="channel-title">
          <Settings v-if="navigation.destination === 'settings'" :size="19" aria-hidden="true" />
          <Radio v-else-if="isServerDestination && activeChannel?.type === 1" :size="19" aria-hidden="true" />
          <Hash v-else :size="19" aria-hidden="true" />
          <span class="channel-title-copy">
            <span>{{ workspaceTitle }}</span>
            <small>{{ workspaceSubtitle }}</small>
          </span>
          <span v-if="voiceLocationSummary" class="channel-location-summary">{{ voiceLocationSummary }}</span>
        </div>
        <div v-if="isServerDestination" class="channel-header-tools" :aria-label="t('app.header.channelTools')">
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.threads')"
            :aria-label="t('app.header.threads')"
            :aria-expanded="activeHeaderPanel === 'threads'"
            @click="toggleHeaderPanel('threads')"
          >
            <List :size="17" aria-hidden="true" />
          </button>
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
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.inbox')"
            :aria-label="t('app.header.inbox')"
            @click="showHeaderPlaceholder(t('app.header.inbox'))"
          >
            <Inbox :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            :title="t('app.header.help')"
            :aria-label="t('app.header.help')"
            @click="showHeaderPlaceholder(t('app.header.help'))"
          >
            <CircleHelp :size="17" aria-hidden="true" />
          </button>
        </div>
        <div class="session-state" :class="gatewayStatus">
          <Wifi v-if="gatewayStatus === 'connected'" :size="17" aria-hidden="true" />
          <WifiOff v-else :size="17" aria-hidden="true" />
          <span>{{ statusLabel }}</span>
        </div>
        <div class="topbar-actions">
          <button
            class="topbar-icon-button"
            type="button"
            :aria-label="t('app.header.createInvite')"
            :disabled="!activeGuild || isInviteWorking"
            v-if="isServerDestination"
            @click="handleCreateInvite"
          >
            <Link :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            :aria-label="t('app.header.joinServer')"
            v-if="isServerDestination"
            @click="openJoinGuild"
          >
            <LogIn :size="17" aria-hidden="true" />
          </button>
          <button class="topbar-icon-button" type="button" :aria-label="t('app.header.logout')" @click="handleLogout">
            <LogOut :size="17" aria-hidden="true" />
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
        <div v-else-if="workspaceNotice" class="app-notice" role="status">
          {{ workspaceNotice }}
        </div>
      </div>

      <div v-if="guilds.isLoading || dms.isLoading" class="workspace-loading" role="status">
        {{ t('app.workspace.loading') }}
      </div>

      <SettingsView
        v-if="navigation.destination === 'settings'"
        :current-user="session.user"
        :user-status="userPresenceStatus"
        :muted="voiceRtc.isMuted.value"
        :deafened="isDeafened"
        :input-level="voiceRtc.inputLevel.value"
        :turn-configured="voiceTurnConfigured"
        :voice-connected="guilds.voiceConnected"
        @close="navigation.closeSettings"
        @logout="handleLogout"
      />

      <FriendsHome
        v-else-if="navigation.destination === 'friends'"
        :friends="dms.relationships"
        @message-friend="handleMessageFriend"
      />

      <DirectMessageView
        v-else-if="navigation.destination === 'dm'"
        :dm="selectedDm"
        :current-user="session.user"
        :disabled="dms.isMutating"
        @send="handleSendDmMessage"
      />

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

    <section v-if="showInvite" class="modal-layer" aria-label="Server invite">
      <div class="server-create-dialog">
        <div class="auth-mark">DC</div>
        <div class="invite-output">
          <span>Invite code</span>
          <strong>{{ inviteCode }}</strong>
        </div>
        <div class="dialog-actions single">
          <button type="button" @click="closeInvite">Done</button>
        </div>
      </div>
    </section>

    <VoicePanel
      v-if="navigation.destination !== 'settings'"
      :channel="guilds.voiceChannel"
      :current-user="session.user"
      :user-status="userPresenceStatus"
      :connected="guilds.voiceConnected"
      :participants="guilds.activeVoiceStates"
      :signaling-ready="gatewayStatus === 'connected'"
      :local-speaking="voiceRtc.localSpeaking.value"
      :input-level="voiceRtc.inputLevel.value"
      :muted="voiceRtc.isMuted.value"
      :deafened="isDeafened"
      :screen-sharing="voiceRtc.isScreenSharing.value"
      :quality-stats="voiceRtc.qualityStats.value"
      :turn-configured="voiceTurnConfigured"
      :error="voiceRtc.error.value"
      @toggle="handleToggleVoice"
      @toggle-mute="handleToggleMute"
      @toggle-deafen="handleToggleDeafen"
      @toggle-screen="handleToggleScreenShare"
      @cycle-status="cycleUserPresence"
      @open-settings="handleOpenUserSettings"
    />
    <div
      v-if="navigation.destination !== 'settings' && remoteScreenStreams.length"
      class="screen-share-stage"
      aria-label="Screen shares"
    >
      <VoiceVideoSink
        v-for="remote in remoteScreenStreams"
        :key="remote.userId"
        :stream="remote.stream"
        :label="remote.username ? `${remote.username}'s screen` : `User ${remote.userId}'s screen`"
        :state="remote.connectionState"
      />
    </div>
    <div class="voice-audio-sinks" aria-hidden="true">
      <VoiceAudioSink
        v-for="remote in voiceRtc.remoteStreams.value"
        :key="remote.userId"
        :stream="remote.stream"
      />
    </div>
  </main>
</template>
