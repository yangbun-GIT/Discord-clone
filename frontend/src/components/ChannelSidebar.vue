<script setup lang="ts">
import {
  CalendarDays,
  ChevronDown,
  ChevronRight,
  Hash,
  LogIn,
  LogOut,
  MoreHorizontal,
  Plus,
  Radio,
  Settings,
  UserPlus,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { useI18n } from '../i18n'
import type { Channel, Guild, VoiceState } from '../types'

const props = defineProps<{
  guild: Guild
  activeChannelId: number | null
  voiceStates: VoiceState[]
  connectedVoiceChannelId: number | null
}>()

const emit = defineEmits<{
  select: [channelId: number]
  createChannel: [name: string, type: 0 | 1]
  createInvite: []
  channelSettings: [channelId: number]
  joinVoice: [channelId: number]
  leaveVoice: [channelId: number]
}>()

const createChannelType = ref<0 | 1 | null>(null)
const textCollapsed = ref(false)
const voiceCollapsed = ref(false)
const channelDraft = ref('')
const { t } = useI18n()

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
</script>

<template>
  <aside class="channel-sidebar" :aria-label="t('channel.aria.channels')">
    <div class="guild-heading">
      <span>{{ guild.name }}</span>
      <button type="button" :title="t('channel.aria.serverMenu')" :aria-label="t('channel.aria.serverMenu')">
        <MoreHorizontal :size="18" aria-hidden="true" />
      </button>
    </div>

    <button type="button" class="events-entry">
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
        class="channel-row"
        :class="{ active: channel.id === activeChannelId }"
      >
        <button
          class="channel-button"
          type="button"
          :aria-label="channelIconLabel(channel)"
          @click="$emit('select', channel.id)"
        >
          <Radio :size="17" aria-hidden="true" />
          <span>{{ channel.name }}</span>
        </button>
        <div class="channel-row-actions" aria-label="Channel actions">
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
            v-else
            type="button"
            :title="t('channel.aria.joinVoice')"
            :aria-label="t('channel.aria.joinVoice')"
            @click.stop="$emit('joinVoice', channel.id)"
          >
            <LogIn :size="14" aria-hidden="true" />
          </button>
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
        <div
          v-if="channelVoiceStates(channel.id).length || connectedVoiceChannelId === channel.id"
          class="voice-sidebar-members"
          :aria-label="t('channel.aria.voiceMembers')"
        >
          <span v-if="connectedVoiceChannelId === channel.id" class="voice-sidebar-member self">
            {{ t('channel.you') }}
          </span>
          <span
            v-for="state in channelVoiceStates(channel.id)"
            :key="`${channel.id}:${state.user_id}`"
            class="voice-sidebar-member"
          >
            {{ state.username ?? `User ${state.user_id}` }}
          </span>
        </div>
      </div>
    </div>
  </aside>
</template>
