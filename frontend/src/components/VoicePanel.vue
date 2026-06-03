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

import { useI18n } from '../i18n'
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

const { t } = useI18n()

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
  if (props.userStatus === 'dnd') return t('common.status.dnd')
  if (props.userStatus === 'idle') return t('common.status.idle')
  if (props.userStatus === 'offline') return t('common.status.offline')
  return t('common.status.online')
})
</script>

<template>
  <section class="voice-panel" :aria-label="t('voice.aria.controls')">
    <div class="user-panel">
      <button
        type="button"
        class="user-identity"
        :title="t('settings.status')"
        :aria-label="t('settings.status')"
        @click="$emit('cycleStatus')"
      >
        <span class="user-panel-avatar" :class="userStatus">
          {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
        </span>
        <span class="user-panel-copy">
          <strong>{{ currentUser?.username ?? t('common.demoUser') }}</strong>
          <small><Circle :size="8" aria-hidden="true" />{{ presenceLabel }}</small>
        </span>
      </button>
      <div class="user-panel-actions">
        <button
          type="button"
          :title="muted ? t('voice.unmute') : t('voice.mute')"
          :aria-pressed="muted"
          :disabled="!connected"
          @click="$emit('toggleMute')"
        >
          <MicOff v-if="muted" :size="17" aria-hidden="true" />
          <Mic v-else :size="17" aria-hidden="true" />
        </button>
        <button
          type="button"
          :title="deafened ? t('voice.undeafen') : t('voice.deafen')"
          :aria-pressed="deafened"
          @click="$emit('toggleDeafen')"
        >
          <HeadphoneOff v-if="deafened" :size="17" aria-hidden="true" />
          <Headphones v-else :size="17" aria-hidden="true" />
        </button>
        <button
          type="button"
          :title="t('voice.userSettings')"
          :aria-label="t('voice.userSettings')"
          @click="$emit('openSettings')"
        >
          <Settings :size="17" aria-hidden="true" />
        </button>
      </div>
    </div>

    <div v-if="connected" class="voice-connection-card">
      <Radio :size="18" aria-hidden="true" />
      <div>
        <span>{{ channel?.name ?? 'voice-room' }}</span>
        <small>{{ connected ? t('common.status.connected') : t('common.status.disconnected') }}</small>
      </div>
    </div>
    <div v-else class="voice-connection-idle">
      <Radio :size="16" aria-hidden="true" />
      <div>
        <span>{{ channel?.name ?? 'voice-room' }}</span>
        <small>{{ t('common.status.disconnected') }}</small>
      </div>
    </div>
    <div class="voice-presence" aria-live="polite">
      <span>{{ t('voice.onlineCount', { count: participants.length }) }}</span>
      <small v-if="error">{{ error }}</small>
      <small v-else-if="deafened">{{ t('common.status.deafened') }}</small>
      <small v-else-if="muted">{{ t('common.status.muted') }}</small>
      <small v-else-if="localSpeaking" class="speaking">{{ t('voice.speaking') }}</small>
      <small v-else>
        {{
          signalingReady
            ? t('voice.signaling', { ice: turnConfigured ? t('voice.turnReady') : t('voice.stunOnly') })
            : t('voice.gatewayRequired')
        }}
      </small>
      <small v-if="connected" class="voice-quality">{{ qualityLabel }}</small>
      <meter min="0" max="100" :value="inputLevel" :aria-label="t('voice.aria.inputLevel')" />
    </div>
    <div class="voice-actions">
      <button
        type="button"
        class="screen-button"
        :class="{ active: screenSharing }"
        :title="screenSharing ? t('voice.stopScreenShare') : t('voice.screenShare')"
        :disabled="!connected"
        @click="$emit('toggleScreen')"
      >
        <ScreenShareOff v-if="screenSharing" :size="18" aria-hidden="true" />
        <ScreenShare v-else :size="18" aria-hidden="true" />
      </button>
      <button
        type="button"
        class="call-button"
        :class="{ connected }"
        :title="connected ? t('voice.disconnect') : t('voice.connect')"
        @click="$emit('toggle')"
      >
        <PhoneOff v-if="connected" :size="18" aria-hidden="true" />
        <Mic v-else :size="18" aria-hidden="true" />
      </button>
    </div>
  </section>
</template>
