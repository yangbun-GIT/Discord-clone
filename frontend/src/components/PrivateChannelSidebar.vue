<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { MessageCircle, Plus, Search } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import { addDocumentEventListener } from '../services/browserApi'
import type { DirectMessage } from '../types'

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
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null

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
  removeDocumentPointerDown = addDocumentEventListener('mousedown', handleDocumentPointerDown)
  removeDocumentKeyDown = addDocumentEventListener('keydown', handleDocumentKeyDown)
})

onBeforeUnmount(() => {
  removeDocumentPointerDown?.()
  removeDocumentKeyDown?.()
  removeDocumentPointerDown = null
  removeDocumentKeyDown = null
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
          <span class="dm-avatar">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
          <span>
            <strong>{{ dm.display_name }}</strong>
            <small v-if="dm.is_group">{{ t('channel.dm.members', { count: dm.member_count }) }}</small>
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
        data-context-kind="friends-home"
        :data-context-label="t('channel.friends')"
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
      <div
        v-for="dm in dms"
        :key="dm.id"
        class="dm-row-wrap"
      >
        <button
          type="button"
          class="dm-row"
          :class="{ active: activeDestination === 'dm' && dm.id === activeDmId }"
          :aria-current="activeDestination === 'dm' && dm.id === activeDmId ? 'page' : undefined"
          data-context-kind="dm-row"
          :data-context-id="dm.id"
          :data-context-label="dm.display_name"
          @click="$emit('openDm', dm.id)"
        >
          <span class="dm-avatar-wrap">
            <span class="dm-avatar">{{ dm.display_name.slice(0, 1).toUpperCase() }}</span>
          </span>
          <span class="dm-copy">
            <span class="dm-title-line">
              <strong>{{ dm.display_name }}</strong>
              <small v-if="dm.is_group">{{ t('channel.dm.members', { count: dm.member_count }) }}</small>
            </span>
            <span v-if="dm.is_group" class="dm-state-line">
              <small>{{ t('channel.dm.members', { count: dm.member_count }) }}</small>
            </span>
          </span>
          <span v-if="dm.unread_count" class="dm-badge">{{ unreadLabel(dm.unread_count) }}</span>
        </button>
      </div>
    </section>
  </aside>
</template>
