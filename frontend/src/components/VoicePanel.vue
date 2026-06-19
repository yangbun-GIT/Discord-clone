<script setup lang="ts">
import { computed } from 'vue'
import {
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
import type { Channel, User, UserPresenceStatus, VoiceQualityStats } from '../types'

const props = defineProps<{
  channel: Channel | null
  currentUser: User | null
  userStatus: UserPresenceStatus
  connected: boolean
  connectedGuildName: string | null
  connectedElsewhere: boolean
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
  retry: []
  leave: []
  cycleStatus: []
  openSettings: []
}>()

const { t } = useI18n()

const presenceLabel = computed(() => {
  if (props.userStatus === 'dnd') return t('common.status.dnd')
  if (props.userStatus === 'idle') return t('common.status.idle')
  if (props.userStatus === 'offline') return t('common.status.offline')
  return t('common.status.online')
})

const voiceStatusLabel = computed(() => {
  if (props.connectedElsewhere) return t('voice.connectedElsewhere')
  if (props.screenSharing) return t('voice.screenLive')
  return t('common.status.connected')
})

const connectionDetailLabel = computed(() => {
  if (!props.signalingReady) return t('voice.gatewayRequired')
  if (props.qualityStats.connectedPeerCount > 0) {
    return t('voice.peerConnectedCount', { count: props.qualityStats.connectedPeerCount })
  }
  if (props.qualityStats.peerCount > 0) {
    return t('voice.peerConnectingCount', { count: props.qualityStats.peerCount })
  }
  return props.turnConfigured ? t('voice.turnReady') : t('voice.stunOnly')
})

</script>

<template>
  <section
    class="voice-panel"
    :class="{ connected, speaking: localSpeaking, error: Boolean(error) }"
    :aria-label="t('voice.aria.controls')"
  >
    <div
      v-if="connected"
      class="voice-connection-card"
      :class="{ elsewhere: connectedElsewhere }"
      data-context-kind="voice-session"
      :data-context-label="`${connectedGuildName ?? ''} ${channel?.name ?? ''}`.trim()"
    >
      <div class="voice-connection-main">
        <Radio :size="18" aria-hidden="true" />
        <div>
          <span>{{ connectedGuildName ? `${connectedGuildName} / ${channel?.name ?? 'voice-room'}` : channel?.name ?? 'voice-room' }}</span>
          <small>
            <span>{{ voiceStatusLabel }}</span>
            <span aria-hidden="true">·</span>
            <span>{{ connectionDetailLabel }}</span>
          </small>
        </div>
      </div>
      <div class="voice-actions">
        <button
          type="button"
          class="screen-button"
          :class="{ active: screenSharing }"
          :title="screenSharing ? t('voice.stopScreenShare') : t('voice.screenShare')"
          :aria-label="screenSharing ? t('voice.stopScreenShare') : t('voice.screenShare')"
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
          :title="connected ? t('voice.disconnect') : t('voice.joinSelected')"
          :aria-label="connected ? t('voice.disconnect') : t('voice.joinSelected')"
          @click="$emit('toggle')"
        >
          <PhoneOff v-if="connected" :size="18" aria-hidden="true" />
          <Mic v-else :size="18" aria-hidden="true" />
        </button>
      </div>
    </div>

    <section v-if="error" class="voice-error-card" role="alert">
      <div>
        <strong>{{ t('voice.errorTitle') }}</strong>
        <span>{{ error }}</span>
      </div>
      <div class="voice-error-actions">
        <button type="button" @click="$emit('retry')">{{ t('voice.retryCapture') }}</button>
        <button type="button" @click="$emit('openSettings')">{{ t('voice.openVoiceSettings') }}</button>
        <button v-if="connected" type="button" class="danger" @click="$emit('leave')">
          {{ t('voice.leaveSelected') }}
        </button>
      </div>
    </section>

    <div class="user-panel" data-context-kind="user-panel" :data-context-label="currentUser?.username">
      <button
        type="button"
        class="user-identity"
        :title="t('settings.status')"
        :aria-label="t('settings.status')"
        @click="$emit('cycleStatus')"
      >
        <span class="user-panel-avatar" :class="{ speaking: localSpeaking }">
          {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
        </span>
        <span class="user-panel-copy">
          <strong>{{ currentUser?.username ?? t('common.demoUser') }}</strong>
          <small>
            <span class="presence-dot user-panel-presence-dot" :class="userStatus" aria-hidden="true"></span>
            {{ presenceLabel }}
          </small>
        </span>
      </button>
      <div class="user-panel-actions">
        <button
          type="button"
          :title="muted ? t('voice.unmute') : t('voice.mute')"
          :aria-label="muted ? t('voice.unmute') : t('voice.mute')"
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
          :aria-label="deafened ? t('voice.undeafen') : t('voice.deafen')"
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
  </section>
</template>
