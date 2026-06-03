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
  Shield,
  UserRound,
  X,
} from 'lucide-vue-next'

import type { User, UserPresenceStatus } from '../types'

type SettingsPanel = 'account' | 'profiles' | 'privacy' | 'voice' | 'appearance' | 'keybinds' | 'logout'

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

const panels: Array<{ id: SettingsPanel; label: string; group: 'user' | 'app'; icon: unknown }> = [
  { id: 'account', label: 'My Account', group: 'user', icon: UserRound },
  { id: 'profiles', label: 'Profiles', group: 'user', icon: Brush },
  { id: 'privacy', label: 'Privacy & Safety', group: 'user', icon: Shield },
  { id: 'voice', label: 'Voice & Video', group: 'app', icon: Headphones },
  { id: 'appearance', label: 'Appearance', group: 'app', icon: Monitor },
  { id: 'keybinds', label: 'Keybinds', group: 'app', icon: KeyRound },
  { id: 'logout', label: 'Log Out', group: 'app', icon: LogOut },
]

const activePanelLabel = computed(() => panels.find((panel) => panel.id === activePanel.value)?.label ?? 'Settings')
const statusLabel = computed(() => {
  if (props.userStatus === 'dnd') return 'Do Not Disturb'
  return props.userStatus[0].toUpperCase() + props.userStatus.slice(1)
})
</script>

<template>
  <section class="settings-view" aria-label="User settings">
    <aside class="settings-sidebar" aria-label="Settings navigation">
      <div class="settings-user-card">
        <span class="settings-avatar" :class="userStatus">
          {{ currentUser?.username.slice(0, 2).toUpperCase() ?? 'DC' }}
        </span>
        <div>
          <strong>{{ currentUser?.username ?? 'Demo User' }}</strong>
          <small>{{ statusLabel }}</small>
        </div>
      </div>

      <div class="settings-group" aria-label="User settings">
        <p>User Settings</p>
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

      <div class="settings-group" aria-label="App settings">
        <p>App Settings</p>
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
        <button type="button" class="settings-close-button" title="Close settings" aria-label="Close settings" @click="$emit('close')">
          <X :size="20" aria-hidden="true" />
        </button>
      </header>

      <div v-if="activePanel === 'account'" class="settings-section-grid">
        <section class="settings-card">
          <h2>Account</h2>
          <dl>
            <div>
              <dt>Username</dt>
              <dd>{{ currentUser?.username ?? 'Demo User' }}</dd>
            </div>
            <div>
              <dt>User ID</dt>
              <dd>{{ currentUser?.id ?? 'local-demo' }}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{{ statusLabel }}</dd>
            </div>
          </dl>
        </section>
        <section class="settings-card">
          <h2>Session</h2>
          <dl>
            <div>
              <dt>Mode</dt>
              <dd>Local demo</dd>
            </div>
            <div>
              <dt>State</dt>
              <dd>Saved session</dd>
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
            <h2>{{ currentUser?.username ?? 'Demo User' }}</h2>
            <p>{{ statusLabel }}</p>
          </div>
        </section>
      </div>

      <div v-else-if="activePanel === 'privacy'" class="settings-section-grid">
        <section class="settings-card">
          <h2>Direct Message Safety</h2>
          <label class="settings-toggle">
            <span>Filter message requests from unknown demo users</span>
            <input v-model="dmSafety" type="checkbox" />
          </label>
        </section>
        <section class="settings-card">
          <h2>Server Privacy</h2>
          <dl>
            <div>
              <dt>Invite access</dt>
              <dd>Protected</dd>
            </div>
            <div>
              <dt>Member data</dt>
              <dd>Scoped</dd>
            </div>
          </dl>
        </section>
      </div>

      <div v-else-if="activePanel === 'voice'" class="settings-section-grid">
        <section class="settings-card">
          <h2>Voice State</h2>
          <dl>
            <div>
              <dt>Connection</dt>
              <dd>{{ voiceConnected ? 'Connected' : 'Disconnected' }}</dd>
            </div>
            <div>
              <dt>Microphone</dt>
              <dd>{{ muted ? 'Muted' : 'Ready' }}</dd>
            </div>
            <div>
              <dt>Headphones</dt>
              <dd>{{ deafened ? 'Deafened' : 'Listening' }}</dd>
            </div>
            <div>
              <dt>ICE</dt>
              <dd>{{ turnConfigured ? 'TURN ready' : 'STUN only' }}</dd>
            </div>
          </dl>
        </section>
        <section class="settings-card">
          <h2>Input Level</h2>
          <div class="settings-meter-row">
            <Mic :size="18" aria-hidden="true" />
            <meter min="0" max="100" :value="inputLevel" aria-label="Microphone input level" />
          </div>
        </section>
      </div>

      <div v-else-if="activePanel === 'appearance'" class="settings-section-grid">
        <section class="settings-card">
          <h2>Display</h2>
          <label class="settings-toggle">
            <span>Compact channel and message spacing</span>
            <input v-model="compactMode" type="checkbox" />
          </label>
          <label class="settings-toggle">
            <span>Reduce motion for local transitions</span>
            <input v-model="reduceMotion" type="checkbox" />
          </label>
        </section>
      </div>

      <div v-else-if="activePanel === 'keybinds'" class="settings-section-grid">
        <section class="settings-card">
          <h2>Keyboard Shortcuts</h2>
          <div class="keybind-row"><kbd>Ctrl</kbd><kbd>K</kbd><span>Quick switcher placeholder</span></div>
          <div class="keybind-row"><kbd>Esc</kbd><span>Close overlays</span></div>
          <div class="keybind-row"><kbd>Enter</kbd><span>Send focused composer message</span></div>
        </section>
      </div>

      <div v-else class="settings-section-grid">
        <section class="settings-card logout-card">
          <BellOff :size="28" aria-hidden="true" />
          <h2>Log out of this demo session?</h2>
          <p>This clears local session state and returns to the login screen.</p>
          <button type="button" @click="$emit('logout')">Log Out</button>
        </section>
      </div>
    </article>
  </section>
</template>
