<script setup lang="ts">
import { Gift, MessageCircle, Plus, Search, Sparkles, Store, Target } from 'lucide-vue-next'

import type { DirectMessage } from '../types'

defineProps<{
  dms: DirectMessage[]
  activeDmId: number | null
  activeDestination: 'friends' | 'dm' | 'settings' | 'server_channel' | 'voice_channel'
}>()

defineEmits<{
  openFriends: []
  openDm: [dmId: number]
  createDm: []
}>()
</script>

<template>
  <aside class="private-sidebar" aria-label="Private channels">
    <button class="dm-search-button" type="button">
      <Search :size="15" aria-hidden="true" />
      <span>Find or start a conversation</span>
    </button>

    <nav class="private-nav" aria-label="Private navigation">
      <button
        type="button"
        class="private-nav-button"
        :class="{ active: activeDestination === 'friends' }"
        @click="$emit('openFriends')"
      >
        <MessageCircle :size="18" aria-hidden="true" />
        <span>Friends</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Sparkles :size="18" aria-hidden="true" />
        <span>Nitro</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Store :size="18" aria-hidden="true" />
        <span>Shop</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Target :size="18" aria-hidden="true" />
        <span>Quests</span>
      </button>
    </nav>

    <section class="dm-list-section">
      <div class="dm-list-heading">
        <p>Direct Messages</p>
        <button type="button" aria-label="Create direct message" @click="$emit('createDm')">
          <Plus :size="16" aria-hidden="true" />
        </button>
      </div>
      <button
        v-for="dm in dms"
        :key="dm.id"
        type="button"
        class="dm-row"
        :class="{ active: activeDestination === 'dm' && dm.id === activeDmId }"
        @click="$emit('openDm', dm.id)"
      >
        <span class="dm-avatar" :class="dm.status">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
        <span class="dm-copy">
          <strong>{{ dm.display_name }}</strong>
          <small v-if="dm.is_group">{{ dm.member_count }} members</small>
          <small v-else>{{ dm.activity ?? dm.status }}</small>
        </span>
        <span v-if="dm.unread_count" class="dm-badge">{{ dm.unread_count }}</span>
      </button>
    </section>
  </aside>
</template>
