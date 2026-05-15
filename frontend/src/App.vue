<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Hash, LogOut, Radio, Wifi, WifiOff } from 'lucide-vue-next'

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
const showCreateGuild = ref(false)
const guildName = ref('')

async function openWorkspace() {
  if (!session.token) return
  await guilds.loadGuilds(session.token)
  connectGateway(session.token)
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
      @create-channel="guilds.createChannel(session.token, $event)"
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
        <button class="logout-button" type="button" aria-label="Log out" @click="handleLogout">
          <LogOut :size="17" aria-hidden="true" />
        </button>
      </header>

      <div v-if="authError || workspaceError" class="app-error" role="alert">
        {{ authError ?? workspaceError }}
      </div>

      <div v-if="activeGuild" class="content-grid">
        <ChatView
          :channel="activeChannel"
          :messages="activeMessages"
          :current-user="session.user"
          @send="guilds.sendMessage(session.token, $event)"
        />
        <MemberList v-if="activeGuild" :members="activeGuild.members" />
      </div>

      <section v-else class="empty-workspace" aria-label="No servers">
        <div>No servers</div>
        <button type="button" @click="openCreateGuild">Create server</button>
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
          <button type="submit" :disabled="guildName.trim().length < 2 || isCreatingGuild">
            Create
          </button>
        </div>
      </form>
    </section>

    <VoicePanel
      :channel="guilds.voiceChannel"
      :connected="guilds.voiceConnected"
      @toggle="guilds.toggleVoice"
    />
  </main>
</template>
