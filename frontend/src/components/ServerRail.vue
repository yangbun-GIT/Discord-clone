<script setup lang="ts">
import { MessageCircle, Plus } from 'lucide-vue-next'

import type { Guild } from '../types'

defineProps<{
  guilds: Guild[]
  activeGuildId: number | null
  homeActive: boolean
}>()

defineEmits<{
  home: []
  select: [guildId: number]
  create: []
}>()
</script>

<template>
  <nav class="server-rail" aria-label="Servers">
    <button
      class="server-button home"
      :class="{ active: homeActive }"
      type="button"
      title="Direct Messages"
      aria-label="Direct Messages"
      @click="$emit('home')"
    >
      <MessageCircle :size="22" aria-hidden="true" />
    </button>
    <div class="server-separator" role="separator" aria-hidden="true"></div>
    <button
      v-for="guild in guilds"
      :key="guild.id"
      class="server-button"
      :class="{ active: guild.id === activeGuildId }"
      type="button"
      :title="guild.name"
      @click="$emit('select', guild.id)"
    >
      {{ guild.name.slice(0, 2).toUpperCase() }}
    </button>
    <button class="server-button add" type="button" title="Create server" @click="$emit('create')">
      <Plus :size="22" aria-hidden="true" />
    </button>
  </nav>
</template>
