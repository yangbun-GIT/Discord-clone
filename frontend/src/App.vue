<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Hash, Link, LogIn, LogOut, Radio, Wifi, WifiOff } from 'lucide-vue-next'

import AuthPanel from './components/AuthPanel.vue'
import ChannelSidebar from './components/ChannelSidebar.vue'
import ChatView from './components/ChatView.vue'
import MemberList from './components/MemberList.vue'
import ServerRail from './components/ServerRail.vue'
import VoicePanel from './components/VoicePanel.vue'
import { useGateway } from './composables/useGateway'
import { useGuildStore } from './stores/guilds'
import { useSessionStore } from './stores/session'

const session = useSessionStore()
const guilds = useGuildStore()
const {
  connect: connectGateway,
  disconnect: disconnectGateway,
  status: gatewayStatus,
  statusLabel,
} = useGateway()

const activeGuild = computed(() => guilds.activeGuild)
const activeChannel = computed(() => guilds.activeChannel)
const activeMessages = computed(() => guilds.activeMessages)
const workspaceTitle = computed(() => {
  if (!activeGuild.value) return 'No servers'
  return activeChannel.value?.name ?? 'loading'
})
const isBooting = ref(true)
const authError = ref<string | null>(null)
const workspaceError = ref<string | null>(null)
const isAuthenticating = ref(false)
const isCreatingGuild = ref(false)
const isInviteWorking = ref(false)
const showCreateGuild = ref(false)
const showJoinGuild = ref(false)
const showInvite = ref(false)
const guildName = ref('')
const joinCode = ref('')
const inviteCode = ref<string | null>(null)

async function openWorkspace() {
  if (!session.token) return
  await guilds.loadGuilds(session.token)
  connectGateway(session.token, { onDispatch: guilds.handleGatewayDispatch })
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
  disconnectGateway()
  authError.value = null
  workspaceError.value = null
  session.logout()
  guilds.resetGuilds()
}

function openCreateGuild() {
  workspaceError.value = null
  showCreateGuild.value = true
}

function closeCreateGuild() {
  showCreateGuild.value = false
  guildName.value = ''
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

function handleCreateChannel(name: string) {
  workspaceError.value = null
  void guilds.createChannel(session.token, name).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Channel creation failed'
  })
}

function handleSendMessage(content: string) {
  workspaceError.value = null
  void guilds.sendMessage(session.token, content).catch((error) => {
    workspaceError.value = error instanceof Error ? error.message : 'Message send failed'
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
      @select="guilds.selectGuild"
      @create="openCreateGuild"
    />

    <ChannelSidebar
      v-if="activeGuild"
      :guild="activeGuild"
      :active-channel-id="guilds.activeChannelId"
      @select="guilds.selectChannel"
      @create-channel="handleCreateChannel"
    />

    <section class="workspace">
      <header class="topbar">
        <div class="channel-title">
          <Radio v-if="activeChannel?.type === 1" :size="19" aria-hidden="true" />
          <Hash v-else :size="19" aria-hidden="true" />
          <span>{{ workspaceTitle }}</span>
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
            @click="handleCreateInvite"
          >
            <Link :size="17" aria-hidden="true" />
          </button>
          <button
            class="topbar-icon-button"
            type="button"
            aria-label="Join server"
            @click="openJoinGuild"
          >
            <LogIn :size="17" aria-hidden="true" />
          </button>
          <button class="topbar-icon-button" type="button" aria-label="Log out" @click="handleLogout">
            <LogOut :size="17" aria-hidden="true" />
          </button>
        </div>
      </header>

      <div v-if="authError || workspaceError || guilds.error" class="app-error" role="alert">
        {{ authError ?? workspaceError ?? guilds.error }}
      </div>

      <div v-if="guilds.isLoading" class="workspace-loading" role="status">Loading servers</div>

      <div v-else-if="activeGuild" class="content-grid">
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
          v-if="activeGuild"
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
      :connected="guilds.voiceConnected"
      @toggle="guilds.toggleVoice"
    />
  </main>
</template>
