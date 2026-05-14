<script setup lang="ts">
import { Hash, Plus, Radio } from 'lucide-vue-next'
import { ref } from 'vue'

import type { Guild } from '../types'

defineProps<{
  guild: Guild
  activeChannelId: number | null
}>()

const emit = defineEmits<{
  select: [channelId: number]
  createChannel: [name: string]
}>()

const creatingTextChannel = ref(false)
const channelDraft = ref('')

function openChannelForm() {
  creatingTextChannel.value = true
}

function submitChannel() {
  const name = channelDraft.value.trim()
  if (!name) return
  channelDraft.value = ''
  creatingTextChannel.value = false
  emit('createChannel', name)
}
</script>

<template>
  <aside class="channel-sidebar" aria-label="Channels">
    <div class="guild-heading">
      <span>{{ guild.name }}</span>
    </div>

    <div class="channel-group">
      <div class="channel-group-heading">
        <p>Text Channels</p>
        <button type="button" title="Create text channel" @click="openChannelForm">
          <Plus :size="15" aria-hidden="true" />
        </button>
      </div>
      <form v-if="creatingTextChannel" class="channel-create-form" @submit.prevent="submitChannel">
        <input
          v-model="channelDraft"
          aria-label="Channel name"
          maxlength="100"
          placeholder="new-channel"
        />
        <button type="submit" title="Create channel" :disabled="!channelDraft.trim()">
          <Plus :size="15" aria-hidden="true" />
        </button>
      </form>
      <button
        v-for="channel in guild.channels.filter((item) => item.type === 0)"
        :key="channel.id"
        class="channel-button"
        :class="{ active: channel.id === activeChannelId }"
        type="button"
        @click="$emit('select', channel.id)"
      >
        <Hash :size="17" aria-hidden="true" />
        <span>{{ channel.name }}</span>
      </button>
    </div>

    <div class="channel-group">
      <p>Voice Channels</p>
      <button
        v-for="channel in guild.channels.filter((item) => item.type === 1)"
        :key="channel.id"
        class="channel-button"
        :class="{ active: channel.id === activeChannelId }"
        type="button"
        @click="$emit('select', channel.id)"
      >
        <Radio :size="17" aria-hidden="true" />
        <span>{{ channel.name }}</span>
      </button>
    </div>
  </aside>
</template>
