<script setup lang="ts">
import { computed } from 'vue'
import { Compass, MessageCircle, Plus, Radio } from 'lucide-vue-next'

import type { Guild, ServerRailGuildMeta } from '../types'

const props = defineProps<{
  guilds: Guild[]
  activeGuildId: number | null
  homeActive: boolean
  homeUnreadCount: number
  guildMeta: Record<number, ServerRailGuildMeta>
}>()

defineEmits<{
  home: []
  select: [guildId: number]
  create: []
  discover: []
}>()

const railGroups = computed(() => {
  const groups = new Map<string, { name: string; color: string | null; guilds: Guild[] }>()
  const ungrouped: Guild[] = []

  for (const guild of props.guilds) {
    const meta = props.guildMeta[guild.id]
    if (!meta?.folder_name) {
      ungrouped.push(guild)
      continue
    }
    const key = meta.folder_name
    const existing = groups.get(key)
    if (existing) {
      existing.guilds.push(guild)
    } else {
      groups.set(key, {
        name: key,
        color: meta.folder_color,
        guilds: [guild],
      })
    }
  }

  return {
    ungrouped,
    folders: [...groups.values()],
  }
})

function guildInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.slice(0, 1).toUpperCase())
    .join('')
    || name.slice(0, 2).toUpperCase()
}

function ariaLabelForGuild(guild: Guild) {
  const meta = props.guildMeta[guild.id]
  const details = [
    meta?.muted ? 'muted' : null,
    meta?.mention_count ? `${meta.mention_count} mentions` : null,
    meta?.unread_count ? `${meta.unread_count} unread` : null,
  ].filter(Boolean)
  return details.length ? `${guild.name}, ${details.join(', ')}` : guild.name
}

function badgeLabel(count: number | undefined) {
  if (!count) return ''
  return count > 99 ? '99+' : String(count)
}
</script>

<template>
  <nav class="server-rail" aria-label="Servers">
    <div class="server-slot" :class="{ active: homeActive, unread: homeUnreadCount }">
      <span v-if="homeActive || homeUnreadCount" class="server-unread-pill" aria-hidden="true"></span>
      <button
        class="server-button home"
        :class="{ active: homeActive }"
        type="button"
        title="Direct Messages"
        :aria-label="homeUnreadCount ? `Direct Messages, ${homeUnreadCount} unread` : 'Direct Messages'"
        :aria-current="homeActive ? 'page' : undefined"
        data-context-kind="home"
        data-context-label="Direct Messages"
        @click="$emit('home')"
      >
        <MessageCircle :size="22" aria-hidden="true" />
        <span v-if="homeUnreadCount" class="server-badge">{{ badgeLabel(homeUnreadCount) }}</span>
      </button>
    </div>
    <div class="server-separator" role="separator" aria-hidden="true"></div>

    <template v-for="guild in railGroups.ungrouped" :key="guild.id">
      <div
        class="server-slot"
        :class="{
          active: guild.id === activeGuildId,
          unread: guildMeta[guild.id]?.unread_count && guild.id !== activeGuildId,
          mentioned: guildMeta[guild.id]?.mention_count,
        }"
      >
        <span
          v-if="guild.id === activeGuildId || (guildMeta[guild.id]?.unread_count && guild.id !== activeGuildId)"
          class="server-unread-pill"
          aria-hidden="true"
        ></span>
        <button
          class="server-button"
          :class="{ active: guild.id === activeGuildId, muted: guildMeta[guild.id]?.muted }"
          type="button"
          :title="guild.name"
          :aria-label="ariaLabelForGuild(guild)"
          :aria-current="!homeActive && guild.id === activeGuildId ? 'page' : undefined"
          data-context-kind="server"
          :data-context-label="guild.name"
          @click="$emit('select', guild.id)"
        >
          {{ guildInitials(guild.name) }}
          <span v-if="guildMeta[guild.id]?.mention_count" class="server-badge">
            {{ badgeLabel(guildMeta[guild.id]?.mention_count) }}
          </span>
          <span v-if="guildMeta[guild.id]?.voice_connected" class="server-voice-indicator" aria-label="Voice connected">
            <Radio :size="12" aria-hidden="true" />
          </span>
          <span v-else-if="guildMeta[guild.id]?.muted" class="server-muted-dot" aria-hidden="true"></span>
        </button>
      </div>
    </template>

    <section
      v-for="folder in railGroups.folders"
      :key="folder.name"
      class="server-folder"
      :aria-label="`${folder.name} folder`"
    >
      <div class="server-folder-label" :style="{ borderColor: folder.color ?? undefined }" aria-hidden="true">
        {{ folder.name.slice(0, 2).toUpperCase() }}
      </div>
      <div class="server-folder-stack">
        <div
          v-for="guild in folder.guilds"
          :key="guild.id"
          class="server-slot"
          :class="{
            active: guild.id === activeGuildId,
            unread: guildMeta[guild.id]?.unread_count && guild.id !== activeGuildId,
            mentioned: guildMeta[guild.id]?.mention_count,
          }"
        >
          <span
            v-if="guild.id === activeGuildId || (guildMeta[guild.id]?.unread_count && guild.id !== activeGuildId)"
            class="server-unread-pill"
            aria-hidden="true"
          ></span>
          <button
            class="server-button"
            :class="{ active: guild.id === activeGuildId, muted: guildMeta[guild.id]?.muted }"
            type="button"
            :title="guild.name"
            :aria-label="ariaLabelForGuild(guild)"
            :aria-current="!homeActive && guild.id === activeGuildId ? 'page' : undefined"
            data-context-kind="server"
            :data-context-label="guild.name"
            @click="$emit('select', guild.id)"
          >
            {{ guildInitials(guild.name) }}
            <span v-if="guildMeta[guild.id]?.mention_count" class="server-badge">
              {{ badgeLabel(guildMeta[guild.id]?.mention_count) }}
            </span>
            <span v-if="guildMeta[guild.id]?.voice_connected" class="server-voice-indicator" aria-label="Voice connected">
              <Radio :size="12" aria-hidden="true" />
            </span>
            <span v-else-if="guildMeta[guild.id]?.muted" class="server-muted-dot" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    </section>

    <div class="server-separator" role="separator" aria-hidden="true"></div>
    <button
      class="server-button add"
      type="button"
      title="Create server"
      aria-label="Create server"
      @click="$emit('create')"
    >
      <Plus :size="22" aria-hidden="true" />
    </button>
    <button
      class="server-button discovery"
      type="button"
      title="Explore discoverable servers"
      aria-label="Explore discoverable servers"
      @click="$emit('discover')"
    >
      <Compass :size="21" aria-hidden="true" />
    </button>
  </nav>
</template>
