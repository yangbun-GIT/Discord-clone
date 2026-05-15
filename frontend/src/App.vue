<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Hash, Radio, Wifi, WifiOff } from 'lucide-vue-next'

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
const { connect: connectGateway, status: gatewayStatus, statusLabel } = useGateway()

const activeGuild = computed(() => guilds.activeGuild)
const activeChannel = computed(() => guilds.activeChannel)
const activeMessages = computed(() => guilds.activeMessages)

onMounted(async () => {
  await session.ensureDevSession()
  await guilds.loadGuilds(session.token)
  if (session.token) {
    connectGateway(session.token)
  }
})
</script>

<template>
  <main class="app-shell" aria-label="Discord clone workspace">
    <ServerRail
      :guilds="guilds.guilds"
      :active-guild-id="guilds.activeGuildId"
      @select="guilds.selectGuild"
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
          <Hash v-if="activeChannel?.type === 0" :size="19" aria-hidden="true" />
          <Radio v-else :size="19" aria-hidden="true" />
          <span>{{ activeChannel?.name ?? 'loading' }}</span>
        </div>
        <div class="session-state" :class="gatewayStatus">
          <Wifi v-if="gatewayStatus === 'connected'" :size="17" aria-hidden="true" />
          <WifiOff v-else :size="17" aria-hidden="true" />
          <span>{{ statusLabel }}</span>
        </div>
      </header>

      <div class="content-grid">
        <ChatView
          :channel="activeChannel"
          :messages="activeMessages"
          :current-user="session.user"
          @send="guilds.sendMessage(session.token, $event)"
        />
        <MemberList v-if="activeGuild" :members="activeGuild.members" />
      </div>
    </section>

    <VoicePanel
      :channel="guilds.voiceChannel"
      :connected="guilds.voiceConnected"
      @toggle="guilds.toggleVoice"
    />
  </main>
</template>
