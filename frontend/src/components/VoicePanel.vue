<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  ChevronUp,
  Headphones,
  HeadphoneOff,
  Mic,
  MicOff,
  PhoneOff,
  Radio,
  ScreenShare,
  ScreenShareOff,
  Settings,
  Volume2,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
import { addDocumentEventListener } from '../services/browserApi'
import type { VoiceDeviceList, VoiceDeviceSettings } from '../composables/voiceMedia'
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
  muted: boolean
  deafened: boolean
  screenSharing: boolean
  qualityStats: VoiceQualityStats
  turnConfigured: boolean
  error: string | null
  voiceDeviceSettings: VoiceDeviceSettings
  voiceDevices: VoiceDeviceList
}>()

const emit = defineEmits<{
  toggle: []
  toggleMute: []
  toggleDeafen: []
  toggleScreen: []
  retry: []
  leave: []
  cycleStatus: []
  openSettings: []
  updateVoiceDeviceSettings: [settings: Partial<VoiceDeviceSettings>]
  refreshVoiceDevices: []
}>()

const { t } = useI18n()
const audioMenu = ref<'input' | 'output' | null>(null)
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null

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
function toggleAudioMenu(menu: 'input' | 'output') {
  audioMenu.value = audioMenu.value === menu ? null : menu
  emit('refreshVoiceDevices')
}

function handleDeviceSelect(key: 'inputDeviceId' | 'outputDeviceId', event: Event) {
  const target = event.target
  if (!(target instanceof HTMLSelectElement)) return
  emit('updateVoiceDeviceSettings', { [key]: target.value || null })
}

function handleDeviceRange(
  key: 'inputVolume' | 'outputVolume' | 'inputSensitivity',
  event: Event,
) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', { [key]: Number(target.value) })
}

function handleNoiseGateChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', { noiseGate: target.checked })
}

function handleNoiseSuppressionModeChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLSelectElement)) return
  const mode = target.value
  if (mode !== 'off' && mode !== 'rnnoise') return
  emit('updateVoiceDeviceSettings', {
    noiseSuppressionMode: mode,
    rnnoiseSuppression: mode === 'rnnoise',
  })
}

function openSettings() {
  audioMenu.value = null
  emit('openSettings')
}

function handleDocumentPointerDown(event: MouseEvent) {
  if (!audioMenu.value) return
  const target = event.target
  if (
    target instanceof HTMLElement
    && target.closest('.voice-device-popover, .voice-control-cluster')
  ) {
    return
  }
  audioMenu.value = null
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') audioMenu.value = null
}

onMounted(() => {
  removeDocumentPointerDown = addDocumentEventListener('mousedown', handleDocumentPointerDown)
  removeDocumentKeyDown = addDocumentEventListener('keydown', handleDocumentKeyDown)
})

onBeforeUnmount(() => {
  removeDocumentPointerDown?.()
  removeDocumentKeyDown?.()
  removeDocumentPointerDown = null
  removeDocumentKeyDown = null
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

    <div
      v-if="audioMenu"
      class="voice-device-popover"
      :aria-label="audioMenu === 'input' ? t('voice.inputMenu') : t('voice.outputMenu')"
    >
      <template v-if="audioMenu === 'input'">
        <label class="voice-device-field">
          <span>{{ t('settings.inputDevice') }}</span>
          <select
            :value="voiceDeviceSettings.inputDeviceId ?? ''"
            @change="handleDeviceSelect('inputDeviceId', $event)"
          >
            <option value="">{{ t('settings.defaultDevice') }}</option>
            <option v-for="device in voiceDevices.inputs" :key="device.id" :value="device.id">
              {{ device.label }}
            </option>
          </select>
        </label>
        <label class="voice-device-range">
          <span>{{ t('settings.inputVolume') }}</span>
          <input
            type="range"
            min="0"
            max="100"
            :value="voiceDeviceSettings.inputVolume"
            @input="handleDeviceRange('inputVolume', $event)"
          />
          <strong>{{ voiceDeviceSettings.inputVolume }}%</strong>
        </label>
        <label class="voice-device-range voice-device-sensitivity">
          <span>{{ t('settings.inputSensitivity') }}</span>
          <input
            type="range"
            min="5"
            max="85"
            :value="voiceDeviceSettings.inputSensitivity"
            :aria-label="t('settings.inputSensitivity')"
            @input="handleDeviceRange('inputSensitivity', $event)"
          />
          <strong>{{ voiceDeviceSettings.inputSensitivity }}%</strong>
        </label>
        <label class="voice-device-field">
          <span>{{ t('settings.noiseSuppressionEngine') }}</span>
          <select
            :value="voiceDeviceSettings.noiseSuppressionMode"
            @change="handleNoiseSuppressionModeChange"
          >
            <option value="off">{{ t('settings.noiseSuppressionOff') }}</option>
            <option value="rnnoise">{{ t('settings.rnnoiseSuppression') }}</option>
          </select>
        </label>
        <label class="voice-device-toggle">
          <span>{{ t('settings.noiseGate') }}</span>
          <input
            type="checkbox"
            :checked="voiceDeviceSettings.noiseGate"
            @change="handleNoiseGateChange"
          />
        </label>
      </template>
      <template v-else>
        <label class="voice-device-field">
          <span>{{ t('settings.outputDevice') }}</span>
          <select
            :value="voiceDeviceSettings.outputDeviceId ?? ''"
            @change="handleDeviceSelect('outputDeviceId', $event)"
          >
            <option value="">{{ t('settings.defaultDevice') }}</option>
            <option v-for="device in voiceDevices.outputs" :key="device.id" :value="device.id">
              {{ device.label }}
            </option>
          </select>
        </label>
        <label class="voice-device-range">
          <span>{{ t('settings.outputVolume') }}</span>
          <input
            type="range"
            min="0"
            max="100"
            :value="voiceDeviceSettings.outputVolume"
            @input="handleDeviceRange('outputVolume', $event)"
          />
          <strong>{{ voiceDeviceSettings.outputVolume }}%</strong>
        </label>
      </template>
      <button type="button" class="voice-device-settings-button" @click="openSettings">
        <Settings :size="16" aria-hidden="true" />
        <span>{{ t('settings.voice') }}</span>
      </button>
    </div>

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
        <span class="voice-control-cluster">
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
            class="voice-popover-trigger"
            :title="t('voice.openInputMenu')"
            :aria-label="t('voice.openInputMenu')"
            :aria-expanded="audioMenu === 'input'"
            @click="toggleAudioMenu('input')"
          >
            <ChevronUp :size="13" aria-hidden="true" />
          </button>
        </span>
        <span class="voice-control-cluster">
          <button
            type="button"
            :title="deafened ? t('voice.undeafen') : t('voice.deafen')"
            :aria-label="deafened ? t('voice.undeafen') : t('voice.deafen')"
            :aria-pressed="deafened"
            @click="$emit('toggleDeafen')"
          >
            <HeadphoneOff v-if="deafened" :size="17" aria-hidden="true" />
            <Volume2 v-else-if="connected" :size="17" aria-hidden="true" />
            <Headphones v-else :size="17" aria-hidden="true" />
          </button>
          <button
            type="button"
            class="voice-popover-trigger"
            :title="t('voice.openOutputMenu')"
            :aria-label="t('voice.openOutputMenu')"
            :aria-expanded="audioMenu === 'output'"
            @click="toggleAudioMenu('output')"
          >
            <ChevronUp :size="13" aria-hidden="true" />
          </button>
        </span>
        <button
          type="button"
          :title="t('voice.userSettings')"
          :aria-label="t('voice.userSettings')"
          @click="openSettings"
        >
          <Settings :size="17" aria-hidden="true" />
        </button>
      </div>
    </div>
  </section>
</template>
