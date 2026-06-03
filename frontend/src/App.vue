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
import ServerRail from './components/ServerRail.vue'
import VoiceAudioSink from './components/VoiceAudioSink.vue'
import VoicePanel from './components/VoicePanel.vue'
import VoiceVideoSink from './components/VoiceVideoSink.vue'
import { useGateway } from './composables/useGateway'
import { useVoiceRtc } from './composables/useVoiceRtc'
import { useDmStore } from './stores/dms'
import { useGuildStore } from './stores/guilds'
import { useNavigationStore } from './stores/navigation'
import { useSessionStore } from './stores/session'
import { useStoreStore } from './stores/store'
import type { ServerRailGuildMeta, UserPresenceStatus, VoiceConfig, VoiceIceServer } from './types'

const session = useSessionStore()
const guilds = useGuildStore()
const dms = useDmStore()
const navigation = useNavigationStore()
const store = useStoreStore()
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
  if (navigation.destination === 'friends') return 'Friends'
  if (navigation.destination === 'dm') {
    return dms.getDm(navigation.activeDmId)?.display_name ?? 'Direct Message'
  }
  if (!activeGuild.value) return 'No servers'
  return activeChannel.value?.name ?? 'loading'
})
const isPrivateDestination = computed(() =>
  navigation.destination === 'friends' || navigation.destination === 'dm',
)
const selectedDm = computed(() => dms.getDm(navigation.activeDmId))
const isBooting = ref(true)
const authError = ref<string | null>(null)
const workspaceError = ref<string | null>(null)
const workspaceNotice = ref<string | null>(null)
const isAuthenticating = ref(false)
const isCreatingGuild = ref(false)
const isInviteWorking = ref(false)
const showCreateGuild = ref(false)
const showJoinGuild = ref(false)
const showDiscovery = ref(false)
const showInvite = ref(false)
const showMemberList = ref(true)
const guildName = ref('')
const joinCode = ref('')
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

async function openWorkspace() {
  if (!session.token) return
  await Promise.all([
    guilds.loadGuilds(session.token),
    dms.loadPrivateWorkspace(session.token),
    loadVoiceConfig(),
  ])
  navigation.openFriends()
  connectGateway(session.token, { onDispatch: guilds.handleGatewayDispatch })
}

async function loadVoiceConfig() {
  const config = await apiGet<VoiceConfig>('/api/meta/voice')
  voiceIceServers.value = config.ice_servers
  voiceTurnConfigured.value = config.turn_configured
}

onMounted(async () => {
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
    authError.value = error instanceof Error ? error.message : 'Authentication failed'
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
  navigation.openServerChannel()
  guilds.selectGuild(guildId)
}

function handleOpenFriends() {
  workspaceNotice.value = null
  navigation.openFriends()
}

function handleOpenDm(dmId: number) {
  workspaceNotice.value = null
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
    workspaceError.value = error instanceof Error ? error.message : 'Direct message creation failed'
  }
}

function openCreateGuild() {
  workspaceError.value = null
  workspaceNotice.value = null
  showCreateGuild.value = true
}

function closeCreateGuild() {
  showCreateGuild.value = false
  guildName.value = ''
}

function openDiscovery() {
  workspaceError.value = null
  workspaceNotice.value = null
  showDiscovery.value = true
}

function closeDiscovery() {
  showDiscovery.value = false
}

async function handleCreateGuild() {
  if (!guildName.value.trim()) return
  workspaceError.value = null
  isCreatingGuild.value = true
  try {
    await guilds.createGuild(session.token, guildName.value)
    closeCreateGuild()
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : 'Server creation failed'
  } finally {
    isCreatingGuild.value = false
  }
}

function handleCreateChannel(name: string, type: 0 | 1 = 0) {
  workspaceError.value = null
  workspaceNotice.value = null
  void guilds.createChannel(session.token, name, type).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Channel creation failed'
  })
}

function showHeaderPlaceholder(label: string) {
  workspaceError.value = null
  workspaceNotice.value = `${label} is wired as a local app-shell control for this stage.`
}

function handleChannelSettings() {
  showHeaderPlaceholder('Channel settings')
}

function handleSendMessage(content: string) {
  workspaceError.value = null
  void guilds.sendMessage(session.token, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Message send failed'
  })
}

function handleSendDmMessage(content: string) {
  if (!selectedDm.value) return
  workspaceError.value = null
  void dms.sendDmMessage(session.token, selectedDm.value.id, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Direct message send failed'
  })
}

function handleEditMessage(messageId: number, content: string) {
  workspaceError.value = null
  void guilds.editMessage(session.token, messageId, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Message edit failed'
  })
}

function handleDeleteMessage(messageId: number) {
  workspaceError.value = null
  void guilds.deleteMessage(session.token, messageId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Message deletion failed'
  })
}

function handleCreateRole(name: string, permissions: number) {
  workspaceError.value = null
  void guilds.createRole(session.token, name, permissions).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Role creation failed'
  })
}

function handleAssignRole(memberId: number, roleId: number) {
  workspaceError.value = null
  void guilds.assignRole(session.token, memberId, roleId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Role assignment failed'
  })
}

function handleRemoveRole(memberId: number, roleId: number) {
  workspaceError.value = null
  void guilds.removeRole(session.token, memberId, roleId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Role removal failed'
  })
}

function handleRefreshMembers() {
  workspaceError.value = null
  void guilds.refreshActiveGuild(session.token).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Member refresh failed'
  })
}

function handleRemoveMember(memberId: number) {
  workspaceError.value = null
  void guilds.removeMember(session.token, memberId).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Member removal failed'
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
    workspaceError.value = error instanceof Error ? error.message : 'Voice connection failed'
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
  showHeaderPlaceholder('User settings')
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
    workspaceError.value = error instanceof Error ? error.message : 'Screen sharing failed'
  })
}

watch(
  () => guilds.activeVoiceStates.map((state) => `${state.user_id}:${state.channel_id}`).join('|'),
  () => {
    if (!voiceRtc.isCapturing.value || !session.user) return
    void voiceRtc.syncParticipants(guilds.activeVoiceStates).catch((error) => {
      workspaceError.value = error instanceof Error ? error.message : 'Voice peer sync failed'
    })
  },
)

watch(
  () => guilds.lastVoiceSignal,
  (signal) => {
    if (!signal) return
    void voiceRtc.handleSignal(signal).catch((error) => {
      workspaceError.value = error instanceof Error ? error.message : 'Voice signal failed'
    })
  },
)

function openJoinGuild() {
  workspaceError.value = null
  showJoinGuild.value = true
}

function closeJoinGuild() {
  showJoinGuild.value = false
  joinCode.value = ''
}

async function handleJoinGuild() {
  if (!joinCode.value.trim()) return
  workspaceError.value = null
  isInviteWorking.value = true
  try {
    await guilds.joinInvite(session.token, joinCode.value)
    closeJoinGuild()
  } catch (error) {
    workspaceError.value = error instanceof Error ? error.message : 'Invite join failed'
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
    workspaceError.value = error instanceof Error ? error.message : 'Invite creation failed'
  } finally {
    isInviteWorking.value = false
  }
}
</script>

<template>
  <div v-if="isBooting" class="boot-screen" role="status">Loading</div>

  <AuthPanel
    v-else-if="!session.token"
    :error="authError"
    :loading="isAuthenticating"
    @login="handleLogin"
    @register="handleRegister"
    @demo="handleDemo"
  />

  <main v-else class="app-shell" aria-label="Discord clone workspace">
    <ServerRail
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
    />

    <ChannelSidebar
      v-else-if="activeGuild"
      :guild="activeGuild"
      :active-channel-id="guilds.activeChannelId"
      :voice-states="guilds.voiceStates"
      :connected-voice-channel-id="connectedVoiceChannelId"
      @select="guilds.selectChannel"
      @create-channel="handleCreateChannel"
      @create-invite="handleCreateInvite"
      @channel-settings="handleChannelSettings"
      @join-voice="handleJoinVoiceChannel"
      @leave-voice="handleLeaveVoiceChannel"
    />

    <section class="workspace">
      <header class="topbar">
        <div class="channel-title">
          <Radio v-if="!isPrivateDestination && activeChannel?.type === 1" :size="19" aria-hidden="true" />
          <Hash v-else :size="19" aria-hidden="true" />
          <span>{{ workspaceTitle }}</span>
        </div>
        <div v-if="!isPrivateDestination" class="channel-header-tools" aria-label="Channel tools">
          <button
            class="topbar-icon-button"
            type="button"
            title="Threads"
            aria-label="Threads"
            @click="showHeaderPlaceholder('Threads')"
          >
            <List :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            title="Notification settings"
            aria-label="Notification settings"
            @click="showHeaderPlaceholder('Notification settings')"
          >
            <Bell :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            title="Pinned messages"
            aria-label="Pinned messages"
            @click="showHeaderPlaceholder('Pinned messages')"
          >
            <Pin :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            title="Toggle member list"
            aria-label="Toggle member list"
            :class="{ active: showMemberList }"
            @click="showMemberList = !showMemberList"
          >
            <Users :size="17" aria-hidden="true" />
          </button>
          <label class="topbar-search">
            <Search :size="15" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search"
              aria-label="Search messages"
              @focus="showHeaderPlaceholder('Search')"
            />
          </label>
          <button
            class="topbar-icon-button"
            type="button"
            title="Inbox"
            aria-label="Inbox"
            @click="showHeaderPlaceholder('Inbox')"
          >
            <Inbox :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            title="Help"
            aria-label="Help"
            @click="showHeaderPlaceholder('Help')"
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
            aria-label="Create invite"
            :disabled="!activeGuild || isInviteWorking"
            v-if="!isPrivateDestination"
            @click="handleCreateInvite"
          >
            <Link :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            aria-label="Join server"
            v-if="!isPrivateDestination"
            @click="openJoinGuild"
          >
            <LogIn :size="17" aria-hidden="true" />
          </button>
          <button class="topbar-icon-button" type="button" aria-label="Log out" @click="handleLogout">
            <LogOut :size="17" aria-hidden="true" />
          </button>
        </div>
      </header>

      <div v-if="authError || workspaceError || guilds.error || dms.error" class="app-error" role="alert">
        {{ authError ?? workspaceError ?? guilds.error ?? dms.error }}
      </div>
      <div v-else-if="workspaceNotice" class="app-notice" role="status">
        {{ workspaceNotice }}
      </div>

      <div v-if="guilds.isLoading || dms.isLoading" class="workspace-loading" role="status">Loading workspace</div>

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

      <section v-else class="empty-workspace" aria-label="No servers">
        <div>No servers</div>
        <div class="empty-actions">
          <button type="button" @click="openCreateGuild">Create server</button>
          <button type="button" @click="openJoinGuild">Join server</button>
        </div>
      </section>
    </section>

    <section v-if="showCreateGuild" class="modal-layer" aria-label="Create server">
      <form class="server-create-dialog" @submit.prevent="handleCreateGuild">
        <div class="auth-mark">DC</div>
        <label>
          <span>Server name</span>
          <input
            v-model="guildName"
            autocomplete="off"
            maxlength="100"
            minlength="2"
            required
            autofocus
          />
        </label>
        <div class="dialog-actions">
          <button type="button" @click="closeCreateGuild">Cancel</button>
          <button type="submit" :disabled="guildName.trim().length < 2 || isCreatingGuild || guilds.isMutating">
            Create
          </button>
        </div>
      </form>
    </section>

    <section v-if="showJoinGuild" class="modal-layer" aria-label="Join server">
      <form class="server-create-dialog" @submit.prevent="handleJoinGuild">
        <div class="auth-mark">DC</div>
        <label>
          <span>Invite code</span>
          <input v-model="joinCode" autocomplete="off" required autofocus />
        </label>
        <div class="dialog-actions">
          <button type="button" @click="closeJoinGuild">Cancel</button>
          <button type="submit" :disabled="!joinCode.trim() || isInviteWorking || guilds.isMutating">
            Join
          </button>
        </div>
      </form>
    </section>

    <section v-if="showDiscovery" class="modal-layer" aria-label="Server discovery">
      <div class="server-create-dialog discovery-dialog">
        <div class="auth-mark">EX</div>
        <div class="discovery-copy">
          <h2>Explore Servers</h2>
          <p>Local discovery opens in Stage 7.9. This entry is wired now so the rail layout is complete.</p>
        </div>
        <div class="discovery-list" aria-label="Preview categories">
          <span>Study groups</span>
          <span>Project rooms</span>
          <span>Voice hangouts</span>
        </div>
        <div class="dialog-actions single">
          <button type="button" @click="closeDiscovery">Done</button>
        </div>
      </div>
    </section>

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
    <div v-if="remoteScreenStreams.length" class="screen-share-stage" aria-label="Screen shares">
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
