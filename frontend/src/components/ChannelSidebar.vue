<script setup lang="ts">
import {
  CalendarDays,
  ChevronDown,
  ChevronRight,
  Hash,
  LogOut,
  MessageCircle,
  MoreHorizontal,
  Pencil,
  Plus,
  Radio,
  Settings,
  UserPlus,
} from 'lucide-vue-next'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { useI18n } from '../i18n'
import { addDocumentEventListener } from '../services/browserApi'
import type { Channel, Guild, VoiceState } from '../types'

const props = defineProps<{
  guild: Guild
  activeChannelId: number | null
  voiceStates: VoiceState[]
  connectedVoiceChannelId: number | null
  currentUserId: number | null
  localSpeaking: boolean
  muted: boolean
  deafened: boolean
}>()

const emit = defineEmits<{
  select: [channelId: number]
  createChannel: [name: string, type: 0 | 1]
  createInvite: []
  channelSettings: [channelId: number]
  joinVoice: [channelId: number]
  leaveVoice: [channelId: number]
  demoNotice: [label: string]
}>()

const createChannelType = ref<0 | 1 | null>(null)
const textCollapsed = ref(false)
const voiceCollapsed = ref(false)
const channelDraft = ref('')
const serverMenuOpen = ref(false)
const { t } = useI18n()
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null

const textChannels = computed(() => propsChannels(0))
const voiceChannels = computed(() => propsChannels(1))

function propsChannels(type: 0 | 1) {
  return props.guild.channels.filter((item) => item.type === type)
}

function openChannelForm(type: 0 | 1) {
  createChannelType.value = type
}

function submitChannel() {
  const name = channelDraft.value.trim()
  if (!name || createChannelType.value === null) return
  const type = createChannelType.value
  channelDraft.value = ''
  createChannelType.value = null
  emit('createChannel', name, type)
}

function closeChannelForm() {
  channelDraft.value = ''
  createChannelType.value = null
}

function channelIconLabel(channel: Channel) {
  return channel.type === 0 ? `# ${channel.name}` : `Voice ${channel.name}`
}

function channelVoiceStates(channelId: number) {
  return props.voiceStates.filter((state) => state.channel_id === channelId)
}

function otherVoiceStates(channelId: number) {
  return channelVoiceStates(channelId).filter((state) => state.user_id !== props.currentUserId)
}

function selfVoiceStatusLabel() {
  if (props.deafened) return t('common.status.deafened')
  if (props.muted) return t('common.status.muted')
  if (props.localSpeaking) return t('voice.speaking')
  return t('common.status.connected')
}

function voiceStateStatusLabel(state: VoiceState) {
  if (state.self_deaf) return t('common.status.deafened')
  if (state.self_mute) return t('common.status.muted')
  return t('common.status.listening')
}

function shouldShowVoiceStatus(state?: VoiceState) {
  if (state) return state.self_deaf || state.self_mute
  return props.localSpeaking || props.muted || props.deafened
}

function voiceMemberInitials(label: string | null | undefined) {
  const text = label?.trim() || t('channel.you')
  const chars = Array.from(text)
  return chars.slice(0, 2).join('').toUpperCase()
}

function toggleServerMenu() {
  serverMenuOpen.value = !serverMenuOpen.value
}

function runServerMenuAction(action: 'invite' | 'text' | 'voice' | 'settings') {
  serverMenuOpen.value = false
  if (action === 'invite') {
    emit('createInvite')
    return
  }
  if (action === 'text') {
    openChannelForm(0)
    return
  }
  if (action === 'voice') {
    openChannelForm(1)
    return
  }
  emit('demoNotice', t('channel.aria.serverMenu'))
}

function selectVoiceChannel(channelId: number) {
  if (props.connectedVoiceChannelId === channelId) {
    emit('select', channelId)
    return
  }
  emit('joinVoice', channelId)
}

function handleDocumentPointerDown(event: MouseEvent) {
  if (!serverMenuOpen.value) return
  const target = event.target
  if (
    target instanceof HTMLElement
    && target.closest('.server-context-menu, .guild-heading > button')
  ) {
    return
  }
  serverMenuOpen.value = false
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') serverMenuOpen.value = false
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
  <aside class="channel-sidebar" :aria-label="t('channel.aria.channels')">
    <div class="guild-heading">
      <span>{{ guild.name }}</span>
      <button
        type="button"
        :title="t('channel.aria.serverMenu')"
        :aria-label="t('channel.aria.serverMenu')"
        :aria-expanded="serverMenuOpen"
        @click.stop="toggleServerMenu"
      >
        <MoreHorizontal :size="18" aria-hidden="true" />
      </button>
      <div v-if="serverMenuOpen" class="server-context-menu" role="menu" @click.stop>
        <button type="button" role="menuitem" @click="runServerMenuAction('invite')">
          <UserPlus :size="15" aria-hidden="true" />
          <span>{{ t('channel.menu.invitePeople') }}</span>
        </button>
        <button type="button" role="menuitem" @click="runServerMenuAction('text')">
          <Hash :size="15" aria-hidden="true" />
          <span>{{ t('channel.menu.createText') }}</span>
        </button>
        <button type="button" role="menuitem" @click="runServerMenuAction('voice')">
          <Radio :size="15" aria-hidden="true" />
          <span>{{ t('channel.menu.createVoice') }}</span>
        </button>
        <button type="button" role="menuitem" @click="runServerMenuAction('settings')">
          <Settings :size="15" aria-hidden="true" />
          <span>{{ t('channel.menu.serverSettings') }}</span>
        </button>
      </div>
    </div>

    <button type="button" class="events-entry" @click="$emit('demoNotice', t('channel.events'))">
      <CalendarDays :size="17" aria-hidden="true" />
      <span>{{ t('channel.events') }}</span>
    </button>

    <div class="channel-group">
      <div class="channel-group-heading">
        <button
          class="channel-collapse-button"
          type="button"
          :aria-expanded="!textCollapsed"
          @click="textCollapsed = !textCollapsed"
        >
          <ChevronDown v-if="!textCollapsed" :size="14" aria-hidden="true" />
          <ChevronRight v-else :size="14" aria-hidden="true" />
          <span>{{ t('channel.textChannels') }}</span>
        </button>
        <button
          type="button"
          :title="t('channel.aria.createText')"
          :aria-label="t('channel.aria.createText')"
          @click="openChannelForm(0)"
        >
          <Plus :size="15" aria-hidden="true" />
        </button>
      </div>
      <form v-if="createChannelType === 0" class="channel-create-form" @submit.prevent="submitChannel">
        <label>
          <span>{{ t('channel.name.text') }}</span>
          <input
            v-model="channelDraft"
            :aria-label="t('channel.name.text')"
            maxlength="100"
            :placeholder="t('channel.placeholder.text')"
            autofocus
          />
        </label>
        <div class="channel-create-actions">
          <button
            type="submit"
            class="primary"
            :title="t('channel.aria.createText')"
            :disabled="!channelDraft.trim()"
          >
            <Plus :size="15" aria-hidden="true" />
            <span>{{ t('channel.create') }}</span>
          </button>
          <button type="button" class="ghost" :title="t('channel.cancel')" @click="closeChannelForm">
            {{ t('channel.cancel') }}
          </button>
        </div>
      </form>
      <div
        v-for="channel in textCollapsed ? [] : textChannels"
        :key="channel.id"
        class="channel-row"
        :class="{ active: channel.id === activeChannelId }"
        :aria-current="channel.id === activeChannelId ? 'page' : undefined"
        data-context-kind="text-channel"
        :data-context-label="channel.name"
      >
        <button
          class="channel-button"
          type="button"
          :aria-label="channelIconLabel(channel)"
          @click="$emit('select', channel.id)"
        >
          <Hash :size="17" aria-hidden="true" />
          <span>{{ channel.name }}</span>
        </button>
        <div class="channel-row-actions" aria-label="Channel actions">
          <button
            type="button"
            :title="t('channel.aria.createInvite')"
            :aria-label="t('channel.aria.createInvite')"
            @click.stop="$emit('createInvite')"
          >
            <UserPlus :size="14" aria-hidden="true" />
          </button>
          <button
            type="button"
            :title="t('channel.aria.settings')"
            :aria-label="t('channel.aria.settings')"
            @click.stop="$emit('channelSettings', channel.id)"
          >
            <Settings :size="14" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>

    <div class="channel-group">
      <div class="channel-group-heading">
        <button
          class="channel-collapse-button"
          type="button"
          :aria-expanded="!voiceCollapsed"
          @click="voiceCollapsed = !voiceCollapsed"
        >
          <ChevronDown v-if="!voiceCollapsed" :size="14" aria-hidden="true" />
          <ChevronRight v-else :size="14" aria-hidden="true" />
          <span>{{ t('channel.voiceChannels') }}</span>
        </button>
        <button
          type="button"
          :title="t('channel.aria.createVoice')"
          :aria-label="t('channel.aria.createVoice')"
          @click="openChannelForm(1)"
        >
          <Plus :size="15" aria-hidden="true" />
        </button>
      </div>
      <form v-if="createChannelType === 1" class="channel-create-form" @submit.prevent="submitChannel">
        <label>
          <span>{{ t('channel.name.voice') }}</span>
          <input
            v-model="channelDraft"
            :aria-label="t('channel.name.voice')"
            maxlength="100"
            :placeholder="t('channel.placeholder.voice')"
            autofocus
          />
        </label>
        <div class="channel-create-actions">
          <button
            type="submit"
            class="primary"
            :title="t('channel.aria.createVoice')"
            :disabled="!channelDraft.trim()"
          >
            <Plus :size="15" aria-hidden="true" />
            <span>{{ t('channel.create') }}</span>
          </button>
          <button type="button" class="ghost" :title="t('channel.cancel')" @click="closeChannelForm">
            {{ t('channel.cancel') }}
          </button>
        </div>
      </form>
      <div
        v-for="channel in voiceCollapsed ? [] : voiceChannels"
        :key="channel.id"
        class="channel-row voice-channel-row"
        :class="{
          active: channel.id === activeChannelId,
          connected: connectedVoiceChannelId === channel.id,
          speaking: connectedVoiceChannelId === channel.id && localSpeaking,
        }"
        :aria-current="channel.id === activeChannelId ? 'page' : undefined"
        data-context-kind="voice-channel"
        :data-context-label="channel.name"
      >
        <button
          class="channel-button"
          type="button"
          :aria-label="channelIconLabel(channel)"
          @click="selectVoiceChannel(channel.id)"
        >
          <Radio :size="17" aria-hidden="true" />
          <span>{{ channel.name }}</span>
          <small v-if="connectedVoiceChannelId === channel.id" class="channel-state-badge">
            {{ t('common.status.connected') }}
          </small>
          <small v-else-if="channel.id === activeChannelId" class="channel-state-badge selected">
            {{ t('voice.selected') }}
          </small>
        </button>
        <div class="channel-row-actions" aria-label="Channel actions">
          <button
            v-if="connectedVoiceChannelId === channel.id"
            type="button"
            :title="t('channel.aria.voiceChat')"
            :aria-label="t('channel.aria.voiceChat')"
            @click.stop="$emit('select', channel.id)"
          >
            <MessageCircle :size="14" aria-hidden="true" />
          </button>
          <button
            v-if="connectedVoiceChannelId === channel.id"
            type="button"
            :title="t('channel.aria.leaveVoice')"
            :aria-label="t('channel.aria.leaveVoice')"
            @click.stop="$emit('leaveVoice', channel.id)"
          >
            <LogOut :size="14" aria-hidden="true" />
          </button>
          <button
            type="button"
            :title="t('channel.aria.settings')"
            :aria-label="t('channel.aria.settings')"
            @click.stop="$emit('channelSettings', channel.id)"
          >
            <Settings :size="14" aria-hidden="true" />
          </button>
        </div>
        <div
          v-if="channelVoiceStates(channel.id).length || connectedVoiceChannelId === channel.id"
          class="voice-channel-details"
          :aria-label="t('channel.aria.voiceMembers')"
        >
          <button
            v-if="connectedVoiceChannelId === channel.id"
            type="button"
            class="voice-status-link"
            @click.stop="$emit('channelSettings', channel.id)"
          >
            <span>{{ t('channel.voiceStatusSetup') }}</span>
            <Pencil :size="11" aria-hidden="true" />
          </button>
          <button
            v-if="connectedVoiceChannelId === channel.id"
            type="button"
            class="voice-mood-prompt"
            @click.stop="$emit('demoNotice', t('channel.voiceMoodPrompt'))"
          >
            <UserPlus :size="15" aria-hidden="true" />
            <span>{{ t('channel.voiceMoodPrompt') }}</span>
          </button>
          <div class="voice-sidebar-members">
            <span
              v-if="connectedVoiceChannelId === channel.id"
              class="voice-sidebar-member self"
              :class="{ speaking: localSpeaking }"
            >
              <span class="voice-member-avatar">{{ voiceMemberInitials(t('channel.you')) }}</span>
              <span class="voice-member-copy">
                <strong>{{ t('channel.you') }}</strong>
                <small v-if="shouldShowVoiceStatus()" :class="{ speaking: localSpeaking }">
                  {{ selfVoiceStatusLabel() }}
                </small>
              </span>
            </span>
            <span
              v-for="state in otherVoiceStates(channel.id)"
              :key="`${channel.id}:${state.user_id}`"
              class="voice-sidebar-member"
            >
              <span class="voice-member-avatar">{{ voiceMemberInitials(state.username) }}</span>
              <span class="voice-member-copy">
                <strong>{{ state.username ?? `User ${state.user_id}` }}</strong>
                <small v-if="shouldShowVoiceStatus(state)">{{ voiceStateStatusLabel(state) }}</small>
              </span>
            </span>
          </div>
          <button
            v-if="connectedVoiceChannelId === channel.id"
            type="button"
            class="voice-invite-row"
            @click.stop="$emit('createInvite')"
          >
            <span class="voice-invite-icon">
              <UserPlus :size="16" aria-hidden="true" />
            </span>
            <span>{{ t('channel.voiceInvite') }}</span>
            <ChevronRight :size="16" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
