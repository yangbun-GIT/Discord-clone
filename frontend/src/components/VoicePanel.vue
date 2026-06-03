<script setup lang="ts">
import { computed } from 'vue'
import {
  Circle,
  Headphones,
  HeadphoneOff,
  Mic,
  MicOff,
  PhoneOff,
  Radio,
  ScreenShare,
  ScreenShareOff,
  Settings,
} from 'lucide-vue-next'

import type { Channel, User, UserPresenceStatus, VoiceQualityStats, VoiceState } from '../types'

const props = defineProps<{
  channel: Channel | null
  currentUser: User | null
  userStatus: UserPresenceStatus
  connected: boolean
  participants: VoiceState[]
  signalingReady: boolean
  localSpeaking: boolean
  inputLevel: number
  muted: boolean
  deafened: boolean
  screenSharing: boolean
  qualityStats: VoiceQualityStats
  turnConfigured: boolean
  error: string | null
}>()

defineEmits<{
  toggle: []
  toggleMute: []
  toggleDeafen: []
  toggleScreen: []
  cycleStatus: []
  openSettings: []
}>()

const qualityLabel = computed(() => {
  const stats = props.qualityStats
  const rtt = stats.averageRoundTripTimeMs === null ? '--' : `${Math.round(stats.averageRoundTripTimeMs)}ms`
  const jitter = stats.inboundAudioJitterMs === null ? '--' : `${Math.round(stats.inboundAudioJitterMs)}ms`
  const audio = stats.outboundAudioBitrateKbps === null
    ? '--'
    : `${Math.round(stats.outboundAudioBitrateKbps)}kbps`
  const screen = stats.outboundScreenBitrateKbps === null
    ? '--'
    : `${Math.round(stats.outboundScreenBitrateKbps)}kbps`
  return `Peers ${stats.connectedPeerCount}/${stats.peerCount} | RTT ${rtt} | Jitter ${jitter} | Loss ${stats.inboundAudioPacketsLost} | Audio ${audio} | Screen ${screen}`
})

const presenceLabel = computed(() => {
  if (props.userStatus === 'dnd') return 'Do Not Disturb'
  return props.userStatus[0].toUpperCase() + props.userStatus.slice(1)
})
</script>

<template>
  <section class="voice-panel" aria-label="Voice controls">
    <div class="user-panel">
      <button
        type="button"
        class="user-identity"
        title="Change status"
        aria-label="Change status"
        @click="$emit('cycleStatus')"
      >
        <span class="user-panel-avatar" :class="userStatus">
          {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
        </span>
        <span class="user-panel-copy">
          <strong>{{ currentUser?.username ?? 'Demo User' }}</strong>
          <small><Circle :size="8" aria-hidden="true" />{{ presenceLabel }}</small>
        </span>
      </button>
      <div class="user-panel-actions">
        <button
          type="button"
          :title="muted ? 'Unmute microphone' : 'Mute microphone'"
          :aria-pressed="muted"
          :disabled="!connected"
          @click="$emit('toggleMute')"
        >
          <MicOff v-if="muted" :size="17" aria-hidden="true" />
          <Mic v-else :size="17" aria-hidden="true" />
        </button>
        <button
          type="button"
          :title="deafened ? 'Undeafen' : 'Deafen'"
          :aria-pressed="deafened"
          @click="$emit('toggleDeafen')"
        >
          <HeadphoneOff v-if="deafened" :size="17" aria-hidden="true" />
          <Headphones v-else :size="17" aria-hidden="true" />
        </button>
        <button type="button" title="User settings" aria-label="User settings" @click="$emit('openSettings')">
          <Settings :size="17" aria-hidden="true" />
        </button>
      </div>
    </div>

    <div class="voice-copy">
      <Radio :size="17" aria-hidden="true" />
      <div>
        <span>{{ channel?.name ?? 'voice-room' }}</span>
        <small>{{ connected ? 'Connected' : 'Disconnected' }}</small>
      </div>
    </div>
    <div class="voice-presence" aria-live="polite">
      <span>{{ participants.length }} online</span>
      <small v-if="error">{{ error }}</small>
      <small v-else-if="localSpeaking">Speaking</small>
      <small v-else>
        {{ signalingReady ? `Signaling ready | ${turnConfigured ? 'TURN ready' : 'STUN only'}` : 'Gateway required' }}
      </small>
      <small v-if="connected" class="voice-quality">{{ qualityLabel }}</small>
      <meter min="0" max="100" :value="inputLevel" aria-label="Microphone input level" />
    </div>
    <div class="voice-actions">
      <button
        type="button"
        :title="screenSharing ? 'Stop screen share' : 'Share screen'"
        :disabled="!connected"
        @click="$emit('toggleScreen')"
      >
        <ScreenShareOff v-if="screenSharing" :size="18" aria-hidden="true" />
        <ScreenShare v-else :size="18" aria-hidden="true" />
      </button>
      <button type="button" :title="connected ? 'Disconnect voice' : 'Connect voice'" @click="$emit('toggle')">
        <PhoneOff v-if="connected" :size="18" aria-hidden="true" />
        <Mic v-else :size="18" aria-hidden="true" />
      </button>
    </div>
  </section>
</template>
