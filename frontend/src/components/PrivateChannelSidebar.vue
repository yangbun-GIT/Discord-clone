<script setup lang="ts">
import { MessageCircle, Plus, Search } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { DirectMessage, UserPresenceStatus } from '../types'

defineProps<{
  dms: DirectMessage[]
  activeDmId: number | null
  activeDestination: 'friends' | 'dm' | 'settings' | 'server_channel' | 'voice_channel'
}>()

defineEmits<{
  openFriends: []
  openDm: [dmId: number]
  createDm: []
  demoNotice: [label: string]
}>()

const { t } = useI18n()

function statusLabel(status: UserPresenceStatus) {
  return t(`common.status.${status}`)
}

function unreadLabel(count: number) {
  return count > 99 ? '99+' : String(count)
}
</script>

<template>
  <aside class="private-sidebar" :aria-label="t('channel.aria.privateChannels')">
    <button class="dm-search-button" type="button" @click="$emit('demoNotice', t('channel.findConversation'))">
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
        <span class="dm-avatar-wrap">
          <span class="dm-avatar" :class="dm.status">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
          <span class="presence-dot" :class="dm.status" aria-hidden="true"></span>
        </span>
        <span class="dm-copy">
          <span class="dm-title-line">
            <strong>{{ dm.display_name }}</strong>
            <small v-if="dm.is_group">{{ t('channel.dm.members', { count: dm.member_count }) }}</small>
          </span>
          <span v-if="dm.activity" class="dm-state-line">
            <small>{{ statusLabel(dm.status) }}</small>
            <small>{{ dm.activity }}</small>
          </span>
        </span>
        <span v-if="dm.unread_count" class="dm-badge">{{ unreadLabel(dm.unread_count) }}</span>
      </button>
    </section>
  </aside>
</template>
