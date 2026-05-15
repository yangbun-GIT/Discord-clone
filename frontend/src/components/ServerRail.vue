<script setup lang="ts">
import { Plus } from 'lucide-vue-next'

import type { Guild } from '../types'

defineProps<{
  guilds: Guild[]
  activeGuildId: number | null
}>()

defineEmits<{
  select: [guildId: number]
  create: []
}>()
</script>

<template>
  <nav class="server-rail" aria-label="Servers">
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
