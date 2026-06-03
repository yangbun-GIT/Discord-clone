<script setup lang="ts">
import { Gift, MessageCircle, Plus, Search, Sparkles, Store, Target } from 'lucide-vue-next'

import { useI18n } from '../i18n'
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

const { t } = useI18n()
</script>

<template>
  <aside class="private-sidebar" :aria-label="t('channel.aria.privateChannels')">
    <button class="dm-search-button" type="button">
      <Search :size="15" aria-hidden="true" />
      <span>{{ t('channel.findConversation') }}</span>
    </button>

    <nav class="private-nav" :aria-label="t('channel.aria.privateNavigation')">
      <button
        type="button"
        class="private-nav-button"
        :class="{ active: activeDestination === 'friends' }"
        :aria-current="activeDestination === 'friends' ? 'page' : undefined"
        @click="$emit('openFriends')"
      >
        <MessageCircle :size="18" aria-hidden="true" />
        <span>{{ t('channel.friends') }}</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Sparkles :size="18" aria-hidden="true" />
        <span>{{ t('channel.nitro') }}</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Store :size="18" aria-hidden="true" />
        <span>{{ t('channel.shop') }}</span>
      </button>
      <button type="button" class="private-nav-button muted">
        <Target :size="18" aria-hidden="true" />
        <span>{{ t('channel.quests') }}</span>
      </button>
    </nav>

    <section class="dm-list-section">
      <div class="dm-list-heading">
        <p>{{ t('app.status.directMessage') }}</p>
        <button type="button" :aria-label="t('channel.aria.createDm')" @click="$emit('createDm')">
          <Plus :size="16" aria-hidden="true" />
        </button>
      </div>
      <button
        v-for="dm in dms"
        :key="dm.id"
        type="button"
        class="dm-row"
        :class="{ active: activeDestination === 'dm' && dm.id === activeDmId }"
        :aria-current="activeDestination === 'dm' && dm.id === activeDmId ? 'page' : undefined"
        @click="$emit('openDm', dm.id)"
      >
        <span class="dm-avatar" :class="dm.status">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
        <span class="dm-copy">
          <strong>{{ dm.display_name }}</strong>
          <small v-if="dm.is_group">{{ t('channel.dm.members', { count: dm.member_count }) }}</small>
          <small v-else>{{ dm.activity ?? dm.status }}</small>
        </span>
        <span v-if="dm.unread_count" class="dm-badge">{{ dm.unread_count }}</span>
      </button>
    </section>
  </aside>
</template>
