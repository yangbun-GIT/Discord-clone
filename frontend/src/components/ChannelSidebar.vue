<script setup lang="ts">
import {
  CalendarDays,
  ChevronDown,
  ChevronRight,
  Hash,
  MoreHorizontal,
  Plus,
  Radio,
  Settings,
  UserPlus,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'

import type { Channel, Guild } from '../types'

const props = defineProps<{
  guild: Guild
  activeChannelId: number | null
}>()

const emit = defineEmits<{
  select: [channelId: number]
  createChannel: [name: string, type: 0 | 1]
  createInvite: []
  channelSettings: [channelId: number]
}>()

const createChannelType = ref<0 | 1 | null>(null)
const textCollapsed = ref(false)
const voiceCollapsed = ref(false)
const channelDraft = ref('')

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
</script>

<template>
  <aside class="channel-sidebar" aria-label="Channels">
    <div class="guild-heading">
      <span>{{ guild.name }}</span>
      <button type="button" title="Server menu" aria-label="Server menu">
        <MoreHorizontal :size="18" aria-hidden="true" />
      </button>
    </div>

    <button type="button" class="events-entry">
      <CalendarDays :size="17" aria-hidden="true" />
      <span>Events</span>
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
          <span>Text Channels</span>
        </button>
        <button type="button" title="Create text channel" aria-label="Create text channel" @click="openChannelForm(0)">
          <Plus :size="15" aria-hidden="true" />
        </button>
      </div>
      <form v-if="createChannelType === 0" class="channel-create-form" @submit.prevent="submitChannel">
        <input
          v-model="channelDraft"
          aria-label="Channel name"
          maxlength="100"
          placeholder="new-channel"
          autofocus
        />
        <button type="submit" title="Create channel" :disabled="!channelDraft.trim()">
          <Plus :size="15" aria-hidden="true" />
        </button>
        <button type="button" title="Cancel channel creation" @click="closeChannelForm">Cancel</button>
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
          <button type="button" title="Create invite" aria-label="Create invite" @click.stop="$emit('createInvite')">
            <UserPlus :size="14" aria-hidden="true" />
          </button>
          <button
            type="button"
            title="Channel settings"
            aria-label="Channel settings"
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
          <span>Voice Channels</span>
        </button>
        <button type="button" title="Create voice channel" aria-label="Create voice channel" @click="openChannelForm(1)">
          <Plus :size="15" aria-hidden="true" />
        </button>
      </div>
      <form v-if="createChannelType === 1" class="channel-create-form" @submit.prevent="submitChannel">
        <input
          v-model="channelDraft"
          aria-label="Voice channel name"
          maxlength="100"
          placeholder="voice-room"
          autofocus
        />
        <button type="submit" title="Create channel" :disabled="!channelDraft.trim()">
          <Plus :size="15" aria-hidden="true" />
        </button>
        <button type="button" title="Cancel channel creation" @click="closeChannelForm">Cancel</button>
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
          <button type="button" title="Create invite" aria-label="Create invite" @click.stop="$emit('createInvite')">
            <UserPlus :size="14" aria-hidden="true" />
          </button>
          <button
            type="button"
            title="Channel settings"
            aria-label="Channel settings"
            @click.stop="$emit('channelSettings', channel.id)"
          >
            <Settings :size="14" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
