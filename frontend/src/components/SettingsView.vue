<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Accessibility,
  Bell,
  BellOff,
  Clock3,
  Headphones,
  KeyRound,
  LogOut,
  Mic,
  Monitor,
  RefreshCw,
  Shield,
  ScreenShare,
  Volume2,
  UserRound,
  X,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
import { usePreferencesStore } from '../stores/preferences'
import type {
  AppDensity,
  AppTheme,
  FriendRequestPolicy,
  NotificationMode,
  ScreenShareQuality,
  TimeFormat,
} from '../stores/preferences'
import {
  readVoiceProcessingSettings,
  voiceProcessingPreset,
  writeVoiceProcessingSettings,
  type VoiceConstraintSupport,
  type VoiceDeviceList,
  type VoiceDeviceSettings,
  type VoiceProcessingMode,
  type VoiceProcessingSettings,
} from '../composables/voiceMedia'
import type { User, UserPresenceStatus } from '../types'

type SettingsPanel =
  | 'account'
  | 'privacy'
  | 'notifications'
  | 'voice'
  | 'screen'
  | 'appearance'
  | 'accessibility'
  | 'keybinds'
  | 'language'
  | 'logout'

type SettingsGroup = 'account' | 'experience' | 'session'

const props = defineProps<{
  currentUser: User | null
  initialPanel?: SettingsPanel
  userStatus: UserPresenceStatus
  muted: boolean
  deafened: boolean
  inputLevel: number
  turnConfigured: boolean
  voiceConnected: boolean
  constraintSupport: VoiceConstraintSupport
  voiceDeviceSettings: VoiceDeviceSettings
  voiceDevices: VoiceDeviceList
}>()

const emit = defineEmits<{
  close: []
  logout: []
  updateVoiceDeviceSettings: [settings: Partial<VoiceDeviceSettings>]
  refreshVoiceDevices: []
}>()

const activePanel = ref<SettingsPanel>(props.initialPanel ?? 'account')
const voiceProcessing = ref<VoiceProcessingSettings>(readVoiceProcessingSettings())
const { language, setLanguage, t } = useI18n()
const preferences = usePreferencesStore()

watch(() => props.initialPanel, (panel) => {
  if (panel) activePanel.value = panel
})

const settingsGroups = computed<Array<{ id: SettingsGroup; label: string }>>(() => [
  { id: 'account', label: t('settings.groupAccount') },
  { id: 'experience', label: t('settings.groupExperience') },
  { id: 'session', label: t('settings.groupSession') },
])

const panels = computed<Array<{ id: SettingsPanel; label: string; group: SettingsGroup; icon: unknown }>>(() => [
  { id: 'account', label: t('settings.myAccount'), group: 'account', icon: UserRound },
  { id: 'privacy', label: t('settings.privacy'), group: 'account', icon: Shield },
  { id: 'notifications', label: t('settings.notifications'), group: 'account', icon: Bell },
  { id: 'voice', label: t('settings.voice'), group: 'experience', icon: Headphones },
  { id: 'screen', label: t('settings.screenShare'), group: 'experience', icon: ScreenShare },
  { id: 'appearance', label: t('settings.appearance'), group: 'experience', icon: Monitor },
  { id: 'accessibility', label: t('settings.accessibility'), group: 'experience', icon: Accessibility },
  { id: 'keybinds', label: t('settings.keybinds'), group: 'experience', icon: KeyRound },
  { id: 'language', label: t('settings.languageTime'), group: 'experience', icon: Clock3 },
  { id: 'logout', label: t('settings.logout'), group: 'session', icon: LogOut },
])

const activePanelLabel = computed(
  () => panels.value.find((panel) => panel.id === activePanel.value)?.label ?? t('settings.userSettings'),
)
const statusLabel = computed(() => {
  if (props.userStatus === 'dnd') return t('common.status.dnd')
  if (props.userStatus === 'idle') return t('common.status.idle')
  if (props.userStatus === 'offline') return t('common.status.offline')
  return t('common.status.online')
})
const audioProcessingSummary = computed(() => {
  const enabled = [
    props.constraintSupport.echoCancellation && voiceProcessing.value.echoCancellation
      ? t('settings.echoCancellation')
      : null,
    props.constraintSupport.noiseSuppression && voiceProcessing.value.noiseSuppression
      ? t('settings.noiseSuppression')
      : null,
    props.constraintSupport.autoGainControl && voiceProcessing.value.autoGainControl
      ? t('settings.autoGainControl')
      : null,
  ].filter(Boolean)
  return enabled.length ? enabled.join(' / ') : t('common.status.unavailable')
})
const selectedInputDeviceLabel = computed(() => {
  return deviceLabel(props.voiceDevices.inputs, props.voiceDeviceSettings.inputDeviceId, t('settings.defaultDevice'))
})
const selectedOutputDeviceLabel = computed(() => {
  return deviceLabel(props.voiceDevices.outputs, props.voiceDeviceSettings.outputDeviceId, t('settings.defaultDevice'))
})
const inputSensitivityStyle = computed(() => ({
  '--voice-input-level': `${Math.min(100, Math.max(0, props.inputLevel))}%`,
  '--voice-input-threshold': `${Math.min(100, Math.max(0, props.voiceDeviceSettings.inputSensitivity))}%`,
}))

function deviceLabel(
  devices: VoiceDeviceList['inputs'],
  selectedId: string | null,
  fallback: string,
) {
  if (!selectedId) return fallback
  return devices.find((device) => device.id === selectedId)?.label ?? fallback
}

function setVoiceProcessingOption(key: Exclude<keyof VoiceProcessingSettings, 'mode'>, enabled: boolean) {
  voiceProcessing.value = {
    ...voiceProcessing.value,
    mode: 'custom',
    [key]: enabled,
  }
  writeVoiceProcessingSettings(voiceProcessing.value)
}

function setVoiceProcessingMode(mode: Exclude<VoiceProcessingMode, 'custom'>) {
  voiceProcessing.value = voiceProcessingPreset(mode)
  writeVoiceProcessingSettings(voiceProcessing.value)
}

function handleVoiceProcessingChange(key: Exclude<keyof VoiceProcessingSettings, 'mode'>, event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  setVoiceProcessingOption(key, target.checked)
}

function handleVoiceDeviceSelect(key: 'inputDeviceId' | 'outputDeviceId', event: Event) {
  const target = event.target
  if (!(target instanceof HTMLSelectElement)) return
  emit('updateVoiceDeviceSettings', {
    [key]: target.value || null,
  })
}

function handleVoiceDeviceRange(
  key: 'inputVolume' | 'outputVolume' | 'inputSensitivity',
  event: Event,
) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', {
    [key]: Number(target.value),
  })
}

function handleNoiseGateChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', {
    noiseGate: target.checked,
  })
}

function handleNoiseSuppressionModeChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const mode = target.value
  if (mode !== 'off' && mode !== 'rnnoise') return
  emit('updateVoiceDeviceSettings', {
    noiseSuppressionMode: mode,
    rnnoiseSuppression: mode === 'rnnoise',
  })
}

function handleBooleanPreference(
  setter: (enabled: boolean) => void,
  event: Event,
) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  setter(target.checked)
}

function handleThemeChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'dark' && value !== 'darker') return
  preferences.setTheme(value as AppTheme)
}

function handleDensityChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'comfortable' && value !== 'compact') return
  preferences.setDensity(value as AppDensity)
}

function handleNotificationModeChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'all' && value !== 'mentions' && value !== 'none') return
  preferences.setNotificationMode(value as NotificationMode)
}

function handleFriendRequestPolicyChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'everyone' && value !== 'friends_of_friends' && value !== 'none') return
  preferences.setFriendRequestPolicy(value as FriendRequestPolicy)
}

function handleTimeFormatChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'auto' && value !== '24h') return
  preferences.setTimeFormat(value as TimeFormat)
}

function handleScreenShareQualityChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  const value = target.value
  if (value !== 'balanced' && value !== 'sharp' && value !== 'smooth') return
  preferences.setScreenShareQuality(value as ScreenShareQuality)
}
</script>

<template>
  <section class="settings-view" :aria-label="t('settings.userSettings')">
    <button
      type="button"
      class="settings-overlay-close"
      :title="t('settings.close')"
      :aria-label="t('settings.close')"
      @click="emit('close')"
    >
      <X :size="20" aria-hidden="true" />
    </button>
    <aside class="settings-sidebar" :aria-label="t('settings.userSettings')">
      <div class="settings-user-card">
        <span class="settings-avatar" :class="userStatus">
          {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
        </span>
        <div>
          <strong>{{ currentUser?.username ?? t('common.demoUser') }}</strong>
          <small>{{ statusLabel }}</small>
        </div>
      </div>

      <div
        v-for="group in settingsGroups"
        :key="group.id"
        class="settings-group"
        :aria-label="group.label"
      >
        <p>{{ group.label }}</p>
        <button
          v-for="panel in panels.filter((item) => item.group === group.id)"
          :key="panel.id"
          type="button"
          :class="{ active: activePanel === panel.id, danger: panel.id === 'logout' }"
          @click="activePanel = panel.id"
        >
          <component :is="panel.icon" :size="17" aria-hidden="true" />
          <span>{{ panel.label }}</span>
        </button>
      </div>
    </aside>

    <article class="settings-panel" :aria-labelledby="`settings-${activePanel}`">
      <header class="settings-panel-header">
        <div>
          <h1 :id="`settings-${activePanel}`">{{ activePanelLabel }}</h1>
        </div>
      </header>

      <div v-if="activePanel === 'account'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.account') }}</h2>
          <dl>
            <div>
              <dt>{{ t('settings.username') }}</dt>
              <dd>{{ currentUser?.username ?? t('common.demoUser') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.userId') }}</dt>
              <dd>{{ currentUser?.id ?? t('common.status.localDemo') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.status') }}</dt>
              <dd>{{ statusLabel }}</dd>
            </div>
          </dl>
        </section>
        <section class="settings-card profile-preview">
          <span class="settings-avatar large" :class="userStatus">
            {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
          </span>
          <div>
            <h2>{{ t('settings.profilePreview') }}</h2>
            <p>{{ currentUser?.username ?? t('common.demoUser') }} · {{ statusLabel }}</p>
          </div>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.session') }}</h2>
          <dl>
            <div>
              <dt>{{ t('settings.mode') }}</dt>
              <dd>{{ t('common.status.localDemo') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.state') }}</dt>
              <dd>{{ t('common.status.savedSession') }}</dd>
            </div>
          </dl>
        </section>
      </div>

      <div v-else-if="activePanel === 'privacy'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.dmSafety') }}</h2>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.dmSafetyFilter') }}</strong>
              <small>{{ t('settings.dmSafetyFilterDescription') }}</small>
            </span>
            <input
              :checked="preferences.dmSafety"
              type="checkbox"
              @change="handleBooleanPreference(preferences.setDmSafety, $event)"
            />
          </label>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.allowUnknownDms') }}</strong>
              <small>{{ t('settings.allowUnknownDmsDescription') }}</small>
            </span>
            <input
              :checked="preferences.allowUnknownDms"
              type="checkbox"
              @change="handleBooleanPreference(preferences.setAllowUnknownDms, $event)"
            />
          </label>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.showActivityStatus') }}</strong>
              <small>{{ t('settings.showActivityStatusDescription') }}</small>
            </span>
            <input
              :checked="preferences.showActivityStatus"
              type="checkbox"
              @change="handleBooleanPreference(preferences.setShowActivityStatus, $event)"
            />
          </label>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.friendRequestPolicy') }}</h2>
          <p>{{ t('settings.friendRequestPolicyDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.friendRequestPolicy')">
            <label>
              <input
                type="radio"
                name="friend-request-policy"
                value="everyone"
                :checked="preferences.friendRequestPolicy === 'everyone'"
                @change="handleFriendRequestPolicyChange"
              />
              <span>
                <strong>{{ t('settings.friendRequestEveryone') }}</strong>
                <small>{{ t('settings.friendRequestEveryoneDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="friend-request-policy"
                value="friends_of_friends"
                :checked="preferences.friendRequestPolicy === 'friends_of_friends'"
                @change="handleFriendRequestPolicyChange"
              />
              <span>
                <strong>{{ t('settings.friendRequestFriends') }}</strong>
                <small>{{ t('settings.friendRequestFriendsDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="friend-request-policy"
                value="none"
                :checked="preferences.friendRequestPolicy === 'none'"
                @change="handleFriendRequestPolicyChange"
              />
              <span>
                <strong>{{ t('settings.friendRequestNone') }}</strong>
                <small>{{ t('settings.friendRequestNoneDescription') }}</small>
              </span>
            </label>
          </div>
        </section>
      </div>

      <div v-else-if="activePanel === 'notifications'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.notifications') }}</h2>
          <p>{{ t('settings.notificationsDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.notificationMode')">
            <label>
              <input
                type="radio"
                name="settings-notification-mode"
                value="all"
                :checked="preferences.notificationMode === 'all'"
                @change="handleNotificationModeChange"
              />
              <span>
                <strong>{{ t('headerPanel.notifications.all') }}</strong>
                <small>{{ t('settings.notificationAllDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="settings-notification-mode"
                value="mentions"
                :checked="preferences.notificationMode === 'mentions'"
                @change="handleNotificationModeChange"
              />
              <span>
                <strong>{{ t('headerPanel.notifications.mentions') }}</strong>
                <small>{{ t('settings.notificationMentionsDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="settings-notification-mode"
                value="none"
                :checked="preferences.notificationMode === 'none'"
                @change="handleNotificationModeChange"
              />
              <span>
                <strong>{{ t('headerPanel.notifications.none') }}</strong>
                <small>{{ t('settings.notificationNoneDescription') }}</small>
              </span>
            </label>
          </div>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.soundEffects') }}</strong>
              <small>{{ t('settings.soundEffectsDescription') }}</small>
            </span>
            <input
              :checked="preferences.soundEffects"
              type="checkbox"
              @change="handleBooleanPreference(preferences.setSoundEffects, $event)"
            />
          </label>
        </section>
      </div>

      <div v-else-if="activePanel === 'voice'" class="settings-section-grid">
        <section class="settings-card voice-device-card">
          <h2>{{ t('settings.voiceDevices') }}</h2>
          <p>{{ t('settings.voiceDevicesDescription') }}</p>
          <div class="settings-device-grid">
            <label class="settings-field">
              <span>
                <Mic :size="16" aria-hidden="true" />
                {{ t('settings.inputDevice') }}
              </span>
              <select
                class="settings-select"
                :value="voiceDeviceSettings.inputDeviceId ?? ''"
                @focus="$emit('refreshVoiceDevices')"
                @change="handleVoiceDeviceSelect('inputDeviceId', $event)"
              >
                <option value="">{{ t('settings.defaultDevice') }}</option>
                <option v-for="device in voiceDevices.inputs" :key="device.id" :value="device.id">
                  {{ device.label }}
                </option>
              </select>
              <small>{{ selectedInputDeviceLabel }}</small>
            </label>
            <label class="settings-field">
              <span>
                <Volume2 :size="16" aria-hidden="true" />
                {{ t('settings.outputDevice') }}
              </span>
              <select
                class="settings-select"
                :value="voiceDeviceSettings.outputDeviceId ?? ''"
                @focus="$emit('refreshVoiceDevices')"
                @change="handleVoiceDeviceSelect('outputDeviceId', $event)"
              >
                <option value="">{{ t('settings.defaultDevice') }}</option>
                <option v-for="device in voiceDevices.outputs" :key="device.id" :value="device.id">
                  {{ device.label }}
                </option>
              </select>
              <small>{{ selectedOutputDeviceLabel }}</small>
            </label>
          </div>
          <label class="settings-range-row">
            <span>{{ t('settings.inputVolume') }}</span>
            <input
              type="range"
              min="0"
              max="100"
              :value="voiceDeviceSettings.inputVolume"
              @input="handleVoiceDeviceRange('inputVolume', $event)"
            />
            <strong>{{ voiceDeviceSettings.inputVolume }}%</strong>
          </label>
          <label class="settings-range-row">
            <span>{{ t('settings.outputVolume') }}</span>
            <input
              type="range"
              min="0"
              max="100"
              :value="voiceDeviceSettings.outputVolume"
              @input="handleVoiceDeviceRange('outputVolume', $event)"
            />
            <strong>{{ voiceDeviceSettings.outputVolume }}%</strong>
          </label>
          <button type="button" class="settings-secondary-button" @click="$emit('refreshVoiceDevices')">
            <RefreshCw :size="15" aria-hidden="true" />
            <span>{{ t('settings.refreshDevices') }}</span>
          </button>
          <small class="settings-device-note">{{ t('settings.deviceChangeNote') }}</small>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.voice') }}</h2>
          <dl>
            <div>
              <dt>{{ t('settings.connection') }}</dt>
              <dd>{{ voiceConnected ? t('common.status.connected') : t('common.status.disconnected') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.microphone') }}</dt>
              <dd>{{ muted ? t('common.status.muted') : t('common.status.ready') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.headphones') }}</dt>
              <dd>{{ deafened ? t('common.status.deafened') : t('common.status.listening') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.ice') }}</dt>
              <dd>{{ turnConfigured ? t('voice.turnReady') : t('voice.stunOnly') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.audioProcessing') }}</dt>
              <dd>{{ audioProcessingSummary }}</dd>
            </div>
          </dl>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.audioProcessing') }}</h2>
          <p>{{ t('settings.audioProcessingDescription') }}</p>
          <label class="settings-sensitivity-row">
            <span>
              <strong>{{ t('settings.inputSensitivity') }}</strong>
              <small>{{ t('settings.inputLevelWithSensitivity') }}</small>
            </span>
            <span
              class="voice-sensitivity-control"
              :style="inputSensitivityStyle"
            >
              <span class="voice-sensitivity-track" aria-hidden="true">
                <span class="voice-sensitivity-level"></span>
              </span>
              <input
                type="range"
                min="5"
                max="85"
                :value="voiceDeviceSettings.inputSensitivity"
                :aria-label="t('settings.inputSensitivity')"
                @input="handleVoiceDeviceRange('inputSensitivity', $event)"
              />
            </span>
            <strong>{{ t('settings.inputLevelValue', { level: inputLevel, threshold: voiceDeviceSettings.inputSensitivity }) }}</strong>
          </label>
          <p>{{ t('settings.inputSensitivityDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.audioProcessingPreset')">
            <label>
              <input
                type="radio"
                name="voice-processing-mode"
                value="speech-stability"
                :checked="voiceProcessing.mode === 'speech-stability'"
                @change="setVoiceProcessingMode('speech-stability')"
              />
              <span>
                <strong>{{ t('settings.audioPresetSpeech') }}</strong>
                <small>{{ t('settings.audioPresetSpeechDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="voice-processing-mode"
                value="balanced"
                :checked="voiceProcessing.mode === 'balanced'"
                @change="setVoiceProcessingMode('balanced')"
              />
              <span>
                <strong>{{ t('settings.audioPresetBalanced') }}</strong>
                <small>{{ t('settings.audioPresetBalancedDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="voice-processing-mode"
                value="raw"
                :checked="voiceProcessing.mode === 'raw'"
                @change="setVoiceProcessingMode('raw')"
              />
              <span>
                <strong>{{ t('settings.audioPresetRaw') }}</strong>
                <small>{{ t('settings.audioPresetRawDescription') }}</small>
              </span>
            </label>
          </div>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.noiseSuppressionEngine')">
            <label>
              <input
                type="radio"
                name="noise-suppression-mode"
                value="off"
                :checked="voiceDeviceSettings.noiseSuppressionMode === 'off'"
                @change="handleNoiseSuppressionModeChange"
              />
              <span>
                <strong>{{ t('settings.noiseSuppressionOff') }}</strong>
                <small>{{ t('settings.noiseSuppressionOffDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="noise-suppression-mode"
                value="rnnoise"
                :checked="voiceDeviceSettings.noiseSuppressionMode === 'rnnoise'"
                @change="handleNoiseSuppressionModeChange"
              />
              <span>
                <strong>{{ t('settings.rnnoiseSuppression') }}</strong>
                <small>{{ t('settings.rnnoiseSuppressionDescription') }}</small>
              </span>
            </label>
          </div>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.noiseGate') }}</strong>
              <small>{{ t('settings.noiseGateDescription') }}</small>
            </span>
            <input
              type="checkbox"
              :checked="voiceDeviceSettings.noiseGate"
              @change="handleNoiseGateChange"
            />
          </label>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.echoCancellation') }}</strong>
              <small>{{ t('settings.echoCancellationDescription') }}</small>
            </span>
            <input
              type="checkbox"
              :checked="voiceProcessing.echoCancellation"
              :disabled="!constraintSupport.echoCancellation"
              @change="handleVoiceProcessingChange('echoCancellation', $event)"
            />
          </label>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.noiseSuppression') }}</strong>
              <small>{{ t('settings.noiseSuppressionDescription') }}</small>
            </span>
            <input
              type="checkbox"
              :checked="voiceProcessing.noiseSuppression"
              :disabled="!constraintSupport.noiseSuppression"
              @change="handleVoiceProcessingChange('noiseSuppression', $event)"
            />
          </label>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.autoGainControl') }}</strong>
              <small>{{ t('settings.autoGainControlDescription') }}</small>
            </span>
            <input
              type="checkbox"
              :checked="voiceProcessing.autoGainControl"
              :disabled="!constraintSupport.autoGainControl"
              @change="handleVoiceProcessingChange('autoGainControl', $event)"
            />
          </label>
        </section>
      </div>

      <div v-else-if="activePanel === 'screen'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.screenShare') }}</h2>
          <p>{{ t('settings.screenShareDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.screenShareQuality')">
            <label>
              <input
                type="radio"
                name="screen-share-quality"
                value="balanced"
                :checked="preferences.screenShareQuality === 'balanced'"
                @change="handleScreenShareQualityChange"
              />
              <span>
                <strong>{{ t('settings.screenShareBalanced') }}</strong>
                <small>{{ t('settings.screenShareBalancedDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="screen-share-quality"
                value="sharp"
                :checked="preferences.screenShareQuality === 'sharp'"
                @change="handleScreenShareQualityChange"
              />
              <span>
                <strong>{{ t('settings.screenShareSharp') }}</strong>
                <small>{{ t('settings.screenShareSharpDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="screen-share-quality"
                value="smooth"
                :checked="preferences.screenShareQuality === 'smooth'"
                @change="handleScreenShareQualityChange"
              />
              <span>
                <strong>{{ t('settings.screenShareSmooth') }}</strong>
                <small>{{ t('settings.screenShareSmoothDescription') }}</small>
              </span>
            </label>
          </div>
          <small class="settings-device-note">{{ t('settings.screenShareApplyNote') }}</small>
        </section>
      </div>

      <div v-else-if="activePanel === 'appearance'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.appearance') }}</h2>
          <p>{{ t('settings.appearanceDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.theme')">
            <label>
              <input
                type="radio"
                name="app-theme"
                value="dark"
                :checked="preferences.theme === 'dark'"
                @change="handleThemeChange"
              />
              <span>
                <strong>{{ t('settings.themeDark') }}</strong>
                <small>{{ t('settings.themeDarkDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="app-theme"
                value="darker"
                :checked="preferences.theme === 'darker'"
                @change="handleThemeChange"
              />
              <span>
                <strong>{{ t('settings.themeDarker') }}</strong>
                <small>{{ t('settings.themeDarkerDescription') }}</small>
              </span>
            </label>
          </div>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.density')">
            <label>
              <input
                type="radio"
                name="app-density"
                value="comfortable"
                :checked="preferences.density === 'comfortable'"
                @change="handleDensityChange"
              />
              <span>
                <strong>{{ t('settings.densityComfortable') }}</strong>
                <small>{{ t('settings.densityComfortableDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="app-density"
                value="compact"
                :checked="preferences.density === 'compact'"
                @change="handleDensityChange"
              />
              <span>
                <strong>{{ t('settings.densityCompact') }}</strong>
                <small>{{ t('settings.compactSpacing') }}</small>
              </span>
            </label>
          </div>
        </section>
      </div>

      <div v-else-if="activePanel === 'accessibility'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.accessibility') }}</h2>
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.reduceMotion') }}</strong>
              <small>{{ t('settings.reduceMotionDescription') }}</small>
            </span>
            <input
              :checked="preferences.reduceMotion"
              type="checkbox"
              @change="handleBooleanPreference(preferences.setReduceMotion, $event)"
            />
          </label>
          <dl>
            <div>
              <dt>{{ t('settings.sound') }}</dt>
              <dd>{{ t('common.status.scoped') }}</dd>
            </div>
          </dl>
        </section>
      </div>

      <div v-else-if="activePanel === 'keybinds'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.keybinds') }}</h2>
          <div class="keybind-row"><kbd>Ctrl</kbd><kbd>K</kbd><span>{{ t('settings.keybindQuick') }}</span></div>
          <div class="keybind-row"><kbd>Esc</kbd><span>{{ t('settings.keybindClose') }}</span></div>
          <div class="keybind-row"><kbd>Enter</kbd><span>{{ t('settings.keybindSend') }}</span></div>
        </section>
      </div>

      <div v-else-if="activePanel === 'language'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.languageTime') }}</h2>
          <p>{{ t('settings.languageDescription') }}</p>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.language')">
            <label>
              <input
                type="radio"
                name="app-language"
                value="ko"
                :checked="language === 'ko'"
                @change="setLanguage('ko')"
              />
              <span>{{ t('settings.languageKorean') }}</span>
            </label>
            <label>
              <input
                type="radio"
                name="app-language"
                value="en"
                :checked="language === 'en'"
                @change="setLanguage('en')"
              />
              <span>{{ t('settings.languageEnglish') }}</span>
            </label>
          </div>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.timeFormat') }}</h2>
          <div class="settings-radio-list" role="radiogroup" :aria-label="t('settings.timeFormat')">
            <label>
              <input
                type="radio"
                name="time-format"
                value="auto"
                :checked="preferences.timeFormat === 'auto'"
                @change="handleTimeFormatChange"
              />
              <span>
                <strong>{{ t('settings.timeAutomatic') }}</strong>
                <small>{{ t('settings.timeAutomaticDescription') }}</small>
              </span>
            </label>
            <label>
              <input
                type="radio"
                name="time-format"
                value="24h"
                :checked="preferences.timeFormat === '24h'"
                @change="handleTimeFormatChange"
              />
              <span>
                <strong>{{ t('settings.time24') }}</strong>
                <small>{{ t('settings.time24Description') }}</small>
              </span>
            </label>
          </div>
        </section>
      </div>

      <div v-else class="settings-section-grid">
        <section class="settings-card logout-card">
          <BellOff :size="28" aria-hidden="true" />
          <h2>{{ t('settings.logoutTitle') }}</h2>
          <p>{{ t('settings.logoutDescription') }}</p>
          <button type="button" @click="$emit('logout')">{{ t('settings.logoutButton') }}</button>
        </section>
      </div>
    </article>
  </section>
</template>
