<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { MessageCircle, Plus, Search } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { DirectMessage, UserPresenceStatus } from '../types'

const props = defineProps<{
  dms: DirectMessage[]
  activeDmId: number | null
  activeDestination: 'friends' | 'dm' | 'settings' | 'server_channel' | 'voice_channel'
}>()

const emit = defineEmits<{
  openFriends: []
  openDm: [dmId: number]
  createDm: []
  demoNotice: [label: string]
}>()

const { t } = useI18n()
const root = ref<HTMLElement | null>(null)
const searchOpen = ref(false)
const searchQuery = ref('')

const filteredDms = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return props.dms.slice(0, 8)
  return props.dms.filter((dm) =>
    dm.display_name.toLowerCase().includes(query)
    || dm.participants.some((participant) =>
      participant.username.toLowerCase().includes(query)
      || participant.handle.toLowerCase().includes(query),
    ),
  ).slice(0, 8)
})

function statusLabel(status: UserPresenceStatus) {
  return t(`common.status.${status}`)
}

function unreadLabel(count: number) {
  return count > 99 ? '99+' : String(count)
}

function openDmFromSearch(dmId: number) {
  emit('openDm', dmId)
  searchOpen.value = false
  searchQuery.value = ''
}

function handleDocumentPointerDown(event: MouseEvent) {
  if (!searchOpen.value) return
  const target = event.target
  if (target instanceof Node && root.value?.contains(target)) return
  searchOpen.value = false
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') searchOpen.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentPointerDown)
  document.addEventListener('keydown', handleDocumentKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentPointerDown)
  document.removeEventListener('keydown', handleDocumentKeyDown)
})
</script>

<template>
  <aside ref="root" class="private-sidebar" :aria-label="t('channel.aria.privateChannels')">
    <button
      class="dm-search-button"
      type="button"
      :aria-expanded="searchOpen"
      @click="searchOpen = !searchOpen"
    >
      <Search :size="15" aria-hidden="true" />
      <span>{{ t('channel.findConversation') }}</span>
    </button>

    <section v-if="searchOpen" class="quick-switcher-popover" role="dialog" :aria-label="t('channel.findConversation')">
      <label>
        <Search :size="15" aria-hidden="true" />
        <input
          v-model="searchQuery"
          :placeholder="t('channel.findConversation')"
          autocomplete="off"
          autofocus
        />
      </label>
      <div class="quick-switcher-list">
        <button
          v-for="dm in filteredDms"
          :key="dm.id"
          type="button"
          @click="openDmFromSearch(dm.id)"
        >
          <span class="dm-avatar" :class="dm.status">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
          <span>
            <strong>{{ dm.display_name }}</strong>
            <small>{{ dm.activity ?? statusLabel(dm.status) }}</small>
          </span>
        </button>
        <button type="button" class="quick-create" @click="$emit('createDm'); searchOpen = false">
          <Plus :size="15" aria-hidden="true" />
          <span>{{ t('channel.startNewDm') }}</span>
        </button>
      </div>
    </section>

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
