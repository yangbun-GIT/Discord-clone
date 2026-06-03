<script setup lang="ts">
import { computed, ref } from 'vue'
import { MoreHorizontal, Plus, Search, Send } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Friend } from '../types'

const props = defineProps<{
  friends: Friend[]
}>()

defineEmits<{
  messageFriend: [friendId: number]
}>()

const activeTab = ref<'online' | 'all' | 'pending' | 'blocked' | 'add'>('online')
const searchQuery = ref('')
const addFriendName = ref('')
const { t } = useI18n()

const visibleFriends = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return props.friends.filter((friend) => {
    if (activeTab.value === 'online' && friend.status === 'offline') return false
    if (activeTab.value === 'pending' && !friend.relationship.startsWith('pending')) return false
    if (activeTab.value === 'blocked' && friend.relationship !== 'blocked') return false
    if (activeTab.value === 'all' && friend.relationship !== 'friend') return false
    if (activeTab.value === 'add') return false
    if (!query) return true
    return friend.username.toLowerCase().includes(query) || friend.handle.toLowerCase().includes(query)
  })
})

const activeTabLabel = computed(() => {
  if (activeTab.value === 'online') return t('friends.online')
  if (activeTab.value === 'all') return t('friends.all')
  if (activeTab.value === 'pending') return t('friends.pending')
  if (activeTab.value === 'blocked') return t('friends.blocked')
  return t('friends.add')
})
</script>

<template>
  <section class="friends-home" :aria-label="t('friends.title')">
    <header class="friends-header">
      <h1>{{ t('friends.title') }}</h1>
      <div class="friends-tabs" role="tablist" :aria-label="t('friends.title')">
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'online'"
          :class="{ active: activeTab === 'online' }"
          @click="activeTab = 'online'"
        >
          {{ t('friends.online') }}
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'all'"
          :class="{ active: activeTab === 'all' }"
          @click="activeTab = 'all'"
        >
          {{ t('friends.all') }}
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'pending'"
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          {{ t('friends.pending') }}
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'blocked'"
          :class="{ active: activeTab === 'blocked' }"
          @click="activeTab = 'blocked'"
        >
          {{ t('friends.blocked') }}
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'add'"
          :class="{ active: activeTab === 'add' }"
          @click="activeTab = 'add'"
        >
          {{ t('friends.add') }}
        </button>
      </div>
    </header>

    <div v-if="activeTab === 'add'" class="add-friend-panel">
      <h2>{{ t('friends.add') }}</h2>
      <p>{{ t('friends.addDescription') }}</p>
      <form class="add-friend-form" @submit.prevent="addFriendName = ''">
        <input v-model="addFriendName" :placeholder="t('friends.addPlaceholder')" autocomplete="off" />
        <button type="submit" :disabled="!addFriendName.trim()">
          <Plus :size="17" aria-hidden="true" />
        </button>
      </form>
    </div>

    <template v-else>
      <label class="friend-search">
        <Search :size="17" aria-hidden="true" />
        <input v-model="searchQuery" :placeholder="t('friends.search')" autocomplete="off" />
      </label>

      <section class="friend-list" :aria-label="t('friends.listLabel', { tab: activeTabLabel })">
        <h2>
          {{
            activeTab === 'online'
              ? t('friends.onlineCount', { count: visibleFriends.length })
              : t('friends.totalCount', { count: visibleFriends.length })
          }}
        </h2>
        <div v-if="!visibleFriends.length" class="friends-empty">{{ t('friends.empty') }}</div>
        <article v-for="friend in visibleFriends" :key="friend.id" class="friend-row">
          <span class="friend-avatar" :class="friend.status">{{ friend.username.slice(0, 1).toUpperCase() }}</span>
          <span class="friend-copy">
            <strong>{{ friend.username }}</strong>
            <small>{{ friend.activity ?? friend.status }}</small>
          </span>
          <button type="button" :aria-label="t('friends.sendMessage')" @click="$emit('messageFriend', friend.id)">
            <Send :size="17" aria-hidden="true" />
          </button>
          <button type="button" aria-label="More">
            <MoreHorizontal :size="18" aria-hidden="true" />
          </button>
        </article>
      </section>
    </template>
  </section>
</template>
