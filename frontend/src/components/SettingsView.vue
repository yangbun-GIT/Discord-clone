<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  BellOff,
  Brush,
  Headphones,
  KeyRound,
  LogOut,
  Mic,
  Monitor,
  Languages,
  Shield,
  UserRound,
  X,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { User, UserPresenceStatus } from '../types'

type SettingsPanel = 'account' | 'profiles' | 'privacy' | 'voice' | 'appearance' | 'keybinds' | 'language' | 'logout'

const props = defineProps<{
  currentUser: User | null
  userStatus: UserPresenceStatus
  muted: boolean
  deafened: boolean
  inputLevel: number
  turnConfigured: boolean
  voiceConnected: boolean
}>()

defineEmits<{
  close: []
  logout: []
}>()

const activePanel = ref<SettingsPanel>('account')
const compactMode = ref(false)
const reduceMotion = ref(false)
const dmSafety = ref(true)
const { language, setLanguage, t } = useI18n()

const panels = computed<Array<{ id: SettingsPanel; label: string; group: 'user' | 'app'; icon: unknown }>>(() => [
  { id: 'account', label: t('settings.myAccount'), group: 'user', icon: UserRound },
  { id: 'profiles', label: t('settings.profiles'), group: 'user', icon: Brush },
  { id: 'privacy', label: t('settings.privacy'), group: 'user', icon: Shield },
  { id: 'voice', label: t('settings.voice'), group: 'app', icon: Headphones },
  { id: 'appearance', label: t('settings.appearance'), group: 'app', icon: Monitor },
  { id: 'keybinds', label: t('settings.keybinds'), group: 'app', icon: KeyRound },
  { id: 'language', label: t('settings.language'), group: 'app', icon: Languages },
  { id: 'logout', label: t('settings.logout'), group: 'app', icon: LogOut },
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

      <div class="settings-group" :aria-label="t('settings.userSettings')">
        <p>{{ t('settings.userSettings') }}</p>
        <button
          v-for="panel in panels.filter((item) => item.group === 'user')"
          :key="panel.id"
          type="button"
          :class="{ active: activePanel === panel.id }"
          @click="activePanel = panel.id"
        >
          <component :is="panel.icon" :size="17" aria-hidden="true" />
          <span>{{ panel.label }}</span>
        </button>
      </div>

      <div class="settings-group" :aria-label="t('settings.appSettings')">
        <p>{{ t('settings.appSettings') }}</p>
        <button
          v-for="panel in panels.filter((item) => item.group === 'app')"
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
              <dd>{{ currentUser?.id ?? 'local-demo' }}</dd>
            </div>
            <div>
              <dt>{{ t('settings.status') }}</dt>
              <dd>{{ statusLabel }}</dd>
            </div>
          </dl>
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

      <div v-else-if="activePanel === 'profiles'" class="settings-section-grid">
        <section class="settings-card profile-preview">
          <span class="settings-avatar large" :class="userStatus">
            {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
          </span>
          <div>
            <h2>{{ currentUser?.username ?? t('common.demoUser') }}</h2>
            <p>{{ statusLabel }}</p>
          </div>
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
          </dl>
        </section>
        <section class="settings-card">
          <h2>{{ t('settings.inputLevel') }}</h2>
          <div class="settings-meter-row">
            <Mic :size="18" aria-hidden="true" />
            <meter min="0" max="100" :value="inputLevel" :aria-label="t('voice.aria.inputLevel')" />
          </div>
        </section>
      </div>

      <div v-else-if="activePanel === 'appearance'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.appearance') }}</h2>
          <label class="settings-toggle">
            <span>{{ t('settings.compactSpacing') }}</span>
            <input v-model="compactMode" type="checkbox" />
          </label>
          <label class="settings-toggle">
            <span>{{ t('settings.reduceMotion') }}</span>
            <input v-model="reduceMotion" type="checkbox" />
          </label>
        </section>
      </div>

      <div v-else-if="activePanel === 'keybinds'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.keybinds') }}</h2>
          <div class="keybind-row"><kbd>Ctrl</kbd><kbd>K</kbd><span>Quick switcher placeholder</span></div>
          <div class="keybind-row"><kbd>Esc</kbd><span>Close overlays</span></div>
          <div class="keybind-row"><kbd>Enter</kbd><span>Send focused composer message</span></div>
        </section>
      </div>

      <div v-else-if="activePanel === 'language'" class="settings-section-grid">
        <section class="settings-card">
          <h2>{{ t('settings.language') }}</h2>
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
