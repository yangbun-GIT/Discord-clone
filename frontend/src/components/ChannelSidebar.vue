<script setup lang="ts">
import { Hash, Radio } from 'lucide-vue-next'

import type { Guild } from '../types'

defineProps<{
  guild: Guild
  activeChannelId: number | null
}>()

defineEmits<{
  select: [channelId: number]
}>()
</script>

<template>
  <aside class="channel-sidebar" aria-label="Channels">
    <div class="guild-heading">
      <span>{{ guild.name }}</span>
    </div>

    <div class="channel-group">
      <p>Text Channels</p>
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

