<script setup lang="ts">
import { Info, MessageCircle, Plus, Search } from 'lucide-vue-next'

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
      <button type="button" class="private-nav-button scope" @click="$emit('demoNotice', t('channel.cloneScope'))">
        <Info :size="18" aria-hidden="true" />
        <span>
          <strong>{{ t('channel.cloneScope') }}</strong>
          <small>{{ t('channel.cloneScopeSummary') }}</small>
        </span>
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
          <span class="dm-state-line">
            <small>{{ statusLabel(dm.status) }}</small>
            <small v-if="dm.activity">{{ dm.activity }}</small>
            <small v-else-if="!dm.is_group">{{ t('friends.noActivity') }}</small>
          </span>
        </span>
        <span v-if="dm.unread_count" class="dm-badge">{{ dm.unread_count }}</span>
      </button>
    </section>
  </aside>
</template>
