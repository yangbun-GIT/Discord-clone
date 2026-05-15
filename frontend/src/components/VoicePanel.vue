<script setup lang="ts">
import { computed } from 'vue'
import { Mic, MicOff, PhoneOff, Radio, ScreenShare, ScreenShareOff } from 'lucide-vue-next'

import type { Channel, VoiceQualityStats, VoiceState } from '../types'

const props = defineProps<{
  channel: Channel | null
  connected: boolean
  participants: VoiceState[]
  signalingReady: boolean
  localSpeaking: boolean
  inputLevel: number
  muted: boolean
  screenSharing: boolean
  qualityStats: VoiceQualityStats
  turnConfigured: boolean
  error: string | null
}>()

defineEmits<{
  toggle: []
  toggleMute: []
  toggleScreen: []
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
  return `Peers ${stats.connectedPeerCount}/${stats.peerCount} · RTT ${rtt} · Jitter ${jitter} · Loss ${stats.inboundAudioPacketsLost} · Audio ${audio} · Screen ${screen}`
})
</script>

<template>
  <section class="voice-panel" aria-label="Voice controls">
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
        {{ signalingReady ? `Signaling ready · ${turnConfigured ? 'TURN ready' : 'STUN only'}` : 'Gateway required' }}
      </small>
      <small v-if="connected" class="voice-quality">{{ qualityLabel }}</small>
      <meter min="0" max="100" :value="inputLevel" aria-label="Microphone input level" />
    </div>
    <div class="voice-actions">
      <button
        type="button"
        :title="muted ? 'Unmute microphone' : 'Mute microphone'"
        :disabled="!connected"
        @click="$emit('toggleMute')"
      >
        <Mic v-if="muted" :size="18" aria-hidden="true" />
        <MicOff v-else :size="18" aria-hidden="true" />
      </button>
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
