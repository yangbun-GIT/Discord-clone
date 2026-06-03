<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { MoreHorizontal, Plus, Search, Send } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Friend, UserPresenceStatus } from '../types'

const props = defineProps<{
  friends: Friend[]
}>()

defineEmits<{
  messageFriend: [friendId: number]
}>()

const activeTab = ref<'online' | 'all' | 'pending' | 'blocked' | 'add'>('online')
const searchQuery = ref('')
const addFriendName = ref('')
const moreFriendId = ref<number | null>(null)
const selectedFriendId = ref<number | null>(null)
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

const selectedFriend = computed(
  () => visibleFriends.value.find((friend) => friend.id === selectedFriendId.value) ?? visibleFriends.value[0] ?? null,
)

function statusLabel(status: UserPresenceStatus) {
  return t(`common.status.${status}`)
}

function relationshipLabel(friend: Friend) {
  if (friend.relationship === 'pending_incoming') return t('friends.pendingIncoming')
  if (friend.relationship === 'pending_outgoing') return t('friends.pendingOutgoing')
  if (friend.relationship === 'blocked') return t('friends.blocked')
  return t('friends.friend')
}

watch(
  visibleFriends,
  (friends) => {
    if (!friends.length) {
      selectedFriendId.value = null
      return
    }
    if (!friends.some((friend) => friend.id === selectedFriendId.value)) {
      selectedFriendId.value = friends[0].id
    }
  },
  { immediate: true },
)
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
      <div class="friends-content">
        <div class="friends-list-pane">
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
            <article
              v-for="friend in visibleFriends"
              :key="friend.id"
              class="friend-row"
              :class="{ active: selectedFriend?.id === friend.id }"
              @click="selectedFriendId = friend.id"
            >
              <span class="friend-avatar" :class="friend.status">{{ friend.username.slice(0, 1).toUpperCase() }}</span>
              <span class="friend-copy">
                <span class="friend-name-line">
                  <strong>{{ friend.username }}</strong>
                  <small>{{ friend.handle }}</small>
                </span>
                <span class="friend-status-line">
                  <span class="presence-dot" :class="friend.status" aria-hidden="true"></span>
                  <small>{{ statusLabel(friend.status) }}</small>
                  <small class="friend-relationship">{{ relationshipLabel(friend) }}</small>
                </span>
                <small class="friend-activity">{{ friend.activity ?? t('friends.noActivity') }}</small>
              </span>
              <button
                type="button"
                :aria-label="t('friends.sendMessage')"
                @click.stop="$emit('messageFriend', friend.id)"
              >
                <Send :size="17" aria-hidden="true" />
              </button>
              <button
                type="button"
                :aria-label="t('friends.more')"
                :aria-expanded="moreFriendId === friend.id"
                @click.stop="moreFriendId = moreFriendId === friend.id ? null : friend.id"
              >
                <MoreHorizontal :size="18" aria-hidden="true" />
              </button>
              <div v-if="moreFriendId === friend.id" class="friend-local-menu" role="menu">
                <strong>{{ t('friends.profileSummary') }}</strong>
                <span>{{ friend.handle }}</span>
                <small>{{ t('friends.currentActivity') }}: {{ friend.activity ?? t('friends.noActivity') }}</small>
                <button type="button" role="menuitem" @click="$emit('messageFriend', friend.id)">
                  <Send :size="15" aria-hidden="true" />
                  <span>{{ t('friends.sendMessage') }}</span>
                </button>
              </div>
            </article>
          </section>
        </div>

        <aside v-if="selectedFriend" class="friend-activity-panel" :aria-label="t('friends.selectedProfile')">
          <span class="friend-avatar large" :class="selectedFriend.status">
            {{ selectedFriend.username.slice(0, 1).toUpperCase() }}
          </span>
          <div class="friend-activity-copy">
            <h2>{{ selectedFriend.username }}</h2>
            <p>{{ selectedFriend.handle }}</p>
          </div>
          <dl>
            <div>
              <dt>{{ t('friends.statusLabel') }}</dt>
              <dd>
                <span class="presence-dot" :class="selectedFriend.status" aria-hidden="true"></span>
                {{ statusLabel(selectedFriend.status) }}
              </dd>
            </div>
            <div>
              <dt>{{ t('friends.relationship') }}</dt>
              <dd>{{ relationshipLabel(selectedFriend) }}</dd>
            </div>
            <div>
              <dt>{{ t('friends.currentActivity') }}</dt>
              <dd>{{ selectedFriend.activity ?? t('friends.noActivity') }}</dd>
            </div>
          </dl>
          <button type="button" @click="$emit('messageFriend', selectedFriend.id)">
            <Send :size="16" aria-hidden="true" />
            <span>{{ t('friends.sendMessage') }}</span>
          </button>
        </aside>
      </div>
    </template>
  </section>
</template>
