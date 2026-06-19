<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Accessibility,
  BellOff,
  Clock3,
  Headphones,
  KeyRound,
  LogOut,
  Mic,
  Monitor,
  RefreshCw,
  Shield,
  Volume2,
  UserRound,
  X,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
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
  | 'voice'
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
const compactMode = ref(false)
const reduceMotion = ref(false)
const dmSafety = ref(true)
const timeFormat = ref<'auto' | '24h'>('auto')
const voiceProcessing = ref<VoiceProcessingSettings>(readVoiceProcessingSettings())
const { language, setLanguage, t } = useI18n()

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
  { id: 'voice', label: t('settings.voice'), group: 'experience', icon: Headphones },
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

function handleRnnoiseChange(event: Event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) return
  emit('updateVoiceDeviceSettings', {
    rnnoiseSuppression: target.checked,
  })
}
</script>

<template>
  <section class="settings-view" :aria-label="t('settings.userSettings')">
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
        <button
          type="button"
          class="settings-close-button"
          :title="t('settings.close')"
          :aria-label="t('settings.close')"
          @click="$emit('close')"
        >
          <X :size="20" aria-hidden="true" />
        </button>
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
            <span>{{ t('settings.dmSafetyFilter') }}</span>
            <input v-model="dmSafety" type="checkbox" />
          </label>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.serverPrivacy') }}</h2>
          <dl>
            <div>
              <dt>{{ t('settings.inviteAccess') }}</dt>
              <dd>{{ t('common.status.protected') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.memberData') }}</dt>
              <dd>{{ t('common.status.scoped') }}</dd>
            </div>
          </dl>
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
          <label class="settings-toggle">
            <span>
              <strong>{{ t('settings.rnnoiseSuppression') }}</strong>
              <small>{{ t('settings.rnnoiseSuppressionDescription') }}</small>
            </span>
            <input
              type="checkbox"
              :checked="voiceDeviceSettings.rnnoiseSuppression"
              @change="handleRnnoiseChange"
            />
          </label>
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

      <div v-else-if="activePanel === 'appearance'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.appearance') }}</h2>
          <dl>
            <div>
              <dt>{{ t('settings.theme') }}</dt>
              <dd>{{ t('settings.themeDark') }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.density') }}</dt>
              <dd>{{ compactMode ? t('common.status.connected') : t('common.status.ready') }}</dd>
            </div>
          </dl>
          <label class="settings-toggle">
            <span>{{ t('settings.compactSpacing') }}</span>
            <input v-model="compactMode" type="checkbox" />
          </label>
        </section>
      </div>

      <div v-else-if="activePanel === 'accessibility'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.accessibility') }}</h2>
          <label class="settings-toggle">
            <span>{{ t('settings.reduceMotion') }}</span>
            <input v-model="reduceMotion" type="checkbox" />
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
              <input v-model="timeFormat" type="radio" name="time-format" value="auto" />
              <span>{{ t('settings.timeAutomatic') }}</span>
            </label>
            <label>
              <input v-model="timeFormat" type="radio" name="time-format" value="24h" />
              <span>{{ t('settings.time24') }}</span>
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
