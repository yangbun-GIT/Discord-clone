<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  ArrowDownAZ,
  ArrowUpAZ,
  BellOff,
  Check,
  MoreHorizontal,
  Phone,
  Search,
  Send,
  Star,
  UserRound,
  UserMinus,
  UserX,
  X,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
import { addDocumentEventListener } from '../services/browserApi'
import { usePreferencesStore } from '../stores/preferences'
import type { Friend, UserPresenceStatus } from '../types'

const props = defineProps<{
  friends: Friend[]
  disabled?: boolean
  actionNotice?: string | null
  actionError?: string | null
  pendingRequestFocusKey?: number
  resetTabKey?: number
}>()

const emit = defineEmits<{
  messageFriend: [friendId: number]
  addFriend: [username: string]
  acceptFriend: [friendId: number]
  rejectFriend: [friendId: number]
  cancelFriend: [friendId: number]
  removeFriend: [friendId: number]
  blockFriend: [friendId: number]
  unblockFriend: [friendId: number]
  viewProfile: [friendId: number]
  callFriend: [friendId: number]
  toggleMuteFriend: [friendId: number]
}>()

const activeTab = ref<'online' | 'all' | 'pending' | 'blocked' | 'add'>('all')
const sortDirection = ref<'asc' | 'desc'>('asc')
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null
const searchQuery = ref('')
const addFriendName = ref('')
const addFriendResult = ref('')
const addFriendResultTone = ref<'info' | 'success' | 'error'>('info')
const pendingAddFriend = ref(false)
const selectedFriendId = ref<number | null>(null)
const friendMenu = ref<{
  friendId: number
  mode: 'button' | 'context'
  x: number
  y: number
} | null>(null)
const { t } = useI18n()
const preferences = usePreferencesStore()

const visualFriends = computed(() => props.friends)

const friendCounts = computed(() => {
  const friends = visualFriends.value.filter((friend) => friend.relationship === 'friend')
  return {
    all: friends.length,
    online: friends.filter((friend) => friend.status !== 'offline').length,
    pending: visualFriends.value.filter((friend) => friend.relationship.startsWith('pending')).length,
    blocked: visualFriends.value.filter((friend) => friend.relationship === 'blocked').length,
  }
})

const filteredFriends = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return visualFriends.value.filter((friend) => {
    if (activeTab.value === 'online' && (friend.relationship !== 'friend' || friend.status === 'offline')) return false
    if (activeTab.value === 'pending' && !friend.relationship.startsWith('pending')) return false
    if (activeTab.value === 'blocked' && friend.relationship !== 'blocked') return false
    if (activeTab.value === 'all' && friend.relationship !== 'friend') return false
    if (activeTab.value === 'add') return false
    if (!query) return true
    return friend.username.toLowerCase().includes(query) || friend.handle.toLowerCase().includes(query)
  })
})

const visibleFriends = computed(() => sortFriends(filteredFriends.value))

const hasSearchQuery = computed(() => searchQuery.value.trim().length > 0)

const friendGroups = computed(() => {
  if (activeTab.value === 'all') {
    const friends = visibleFriends.value.filter((friend) => friend.relationship === 'friend')
    const favorites = friends.filter((friend) => preferences.isFavoriteFriend(friend.id))
    const others = friends.filter((friend) => !preferences.isFavoriteFriend(friend.id))
    return [
      {
        id: 'favorites',
        label: t('friends.favoritesCount', { count: favorites.length }),
        friends: favorites,
      },
      {
        id: 'friends',
        label: t('friends.totalCount', { count: others.length }),
        friends: others,
      },
    ].filter((group) => group.friends.length > 0)
  }

  if (activeTab.value !== 'pending') {
    return [{
      id: activeTab.value,
      label: activeTab.value === 'online'
        ? t('friends.onlineCount', { count: visibleFriends.value.length })
        : activeTab.value === 'blocked'
          ? t('friends.blockedCount', { count: visibleFriends.value.length })
        : t('friends.totalCount', { count: visibleFriends.value.length }),
      friends: visibleFriends.value,
    }]
  }

  const incoming = visibleFriends.value.filter((friend) => friend.relationship === 'pending_incoming')
  const outgoing = visibleFriends.value.filter((friend) => friend.relationship === 'pending_outgoing')
  return [
    {
      id: 'pending_incoming',
      label: t('friends.pendingIncomingCount', { count: incoming.length }),
      friends: incoming,
    },
    {
      id: 'pending_outgoing',
      label: t('friends.pendingOutgoingCount', { count: outgoing.length }),
      friends: outgoing,
    },
  ].filter((group) => group.friends.length > 0)
})

const emptyCopy = computed(() => {
  if (hasSearchQuery.value) return t('friends.searchEmpty')
  if (activeTab.value === 'pending') return t('friends.pendingEmpty')
  if (activeTab.value === 'online') return t('friends.onlineEmpty')
  if (activeTab.value === 'blocked') return t('friends.blockedEmpty')
  return t('friends.empty')
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

const activeNowFriends = computed(() =>
  sortFriends(visualFriends.value.filter((friend) => (
    friend.relationship === 'friend' && friend.status === 'online'
  ))),
)

const openMenuFriend = computed(() =>
  friendMenu.value ? visualFriends.value.find((friend) => friend.id === friendMenu.value?.friendId) ?? null : null,
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

function sortFriends(friends: Friend[]) {
  return [...friends].sort((left, right) => {
    const result = left.username.localeCompare(right.username, undefined, { sensitivity: 'base' })
    return sortDirection.value === 'asc' ? result : -result
  })
}

function toggleSortDirection() {
  sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
}

function toggleFavorite(friendId: number) {
  preferences.toggleFavoriteFriend(friendId)
}

function submitAddFriend() {
  const handle = addFriendName.value.trim()
  if (!handle) return
  pendingAddFriend.value = true
  addFriendResultTone.value = 'info'
  addFriendResult.value = t('friends.addSending', { handle })
  emit('addFriend', handle)
  addFriendName.value = ''
}

function openFriendMenu(event: MouseEvent, friend: Friend, mode: 'button' | 'context') {
  selectedFriendId.value = friend.id
  const target = event.currentTarget instanceof HTMLElement ? event.currentTarget : null
  const rect = target?.getBoundingClientRect()
  friendMenu.value = {
    friendId: friend.id,
    mode,
    x: mode === 'context' ? event.clientX : rect ? Math.max(12, rect.right - 280) : event.clientX,
    y: mode === 'context' ? event.clientY : rect ? rect.bottom + 6 : event.clientY,
  }
}

function closeFriendMenu() {
  friendMenu.value = null
}

function handleMenuAction(
  action: 'message' | 'profile' | 'call' | 'mute' | 'remove' | 'block' | 'unblock',
) {
  if (action === 'message' && openMenuFriend.value) {
    emit('messageFriend', openMenuFriend.value.id)
  }
  if (action === 'profile' && openMenuFriend.value) {
    emit('viewProfile', openMenuFriend.value.id)
  }
  if (action === 'call' && openMenuFriend.value) {
    emit('callFriend', openMenuFriend.value.id)
  }
  if (action === 'mute' && openMenuFriend.value) {
    emit('toggleMuteFriend', openMenuFriend.value.id)
  }
  if (action === 'remove' && openMenuFriend.value) {
    emit('removeFriend', openMenuFriend.value.id)
  }
  if (action === 'block' && openMenuFriend.value) {
    emit('blockFriend', openMenuFriend.value.id)
  }
  if (action === 'unblock' && openMenuFriend.value) {
    emit('unblockFriend', openMenuFriend.value.id)
  }
  closeFriendMenu()
}

function handleDocumentPointerDown(event: MouseEvent) {
  if (!friendMenu.value) return
  const target = event.target
  if (
    target instanceof HTMLElement
    && target.closest('.friend-local-menu, .friend-menu-trigger')
  ) {
    return
  }
  closeFriendMenu()
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeFriendMenu()
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

watch(
  () => props.actionNotice,
  (notice) => {
    if (!pendingAddFriend.value || !notice) return
    addFriendResult.value = notice
    addFriendResultTone.value = 'success'
    pendingAddFriend.value = false
  },
)

watch(
  () => props.actionError,
  (error) => {
    if (!pendingAddFriend.value || !error) return
    addFriendResult.value = error
    addFriendResultTone.value = 'error'
    pendingAddFriend.value = false
  },
)

watch(
  () => props.pendingRequestFocusKey,
  (key, previousKey) => {
    if (!key || key === previousKey) return
    activeTab.value = 'pending'
  },
)

watch(
  () => props.resetTabKey,
  (key, previousKey) => {
    if (!key || key === previousKey) return
    activeTab.value = 'all'
  },
)
</script>

<template>
  <section class="friends-home" :aria-label="t('friends.title')">
    <header class="friends-header">
      <h1>
        <UserRound :size="18" aria-hidden="true" />
        <span>{{ t('friends.title') }}</span>
      </h1>
      <div class="friends-tabs" role="tablist" :aria-label="t('friends.title')">
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'all'"
          :class="{ active: activeTab === 'all' }"
          @click="activeTab = 'all'"
        >
          <span>{{ t('friends.all') }}</span>
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'online'"
          :class="{ active: activeTab === 'online' }"
          @click="activeTab = 'online'"
        >
          <span>{{ t('friends.online') }}</span>
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeTab === 'pending'"
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          <span>{{ t('friends.pending') }}</span>
          <small v-if="friendCounts.pending">{{ friendCounts.pending }}</small>
        </button>
        <button
          v-if="friendCounts.blocked"
          type="button"
          role="tab"
          :aria-selected="activeTab === 'blocked'"
          :class="{ active: activeTab === 'blocked' }"
          @click="activeTab = 'blocked'"
        >
          <span>{{ t('friends.blocked') }}</span>
          <small>{{ friendCounts.blocked }}</small>
        </button>
        <button
          type="button"
          role="tab"
          class="add-tab"
          :aria-selected="activeTab === 'add'"
          :class="{ active: activeTab === 'add' }"
          @click="activeTab = 'add'"
        >
          <span>{{ t('friends.add') }}</span>
        </button>
      </div>
    </header>

    <div v-if="activeTab === 'add'" class="add-friend-layout">
      <section class="add-friend-panel">
        <div class="add-friend-copy">
          <h2>{{ t('friends.add') }}</h2>
          <p>{{ t('friends.addDescription') }}</p>
        </div>
        <form class="add-friend-form" @submit.prevent="submitAddFriend">
          <input v-model="addFriendName" :placeholder="t('friends.addPlaceholder')" autocomplete="off" />
          <button type="submit" :disabled="props.disabled || !addFriendName.trim()">
            {{ t('friends.addSubmit') }}
          </button>
        </form>
        <p
          v-if="addFriendResult"
          class="add-friend-result"
          :class="addFriendResultTone"
          role="status"
        >
          {{ addFriendResult }}
        </p>
      </section>
    </div>

    <template v-else>
      <div class="friends-content">
        <div class="friends-list-pane">
          <label class="friend-search">
            <Search :size="17" aria-hidden="true" />
            <input v-model="searchQuery" :placeholder="t('friends.search')" autocomplete="off" />
          </label>
          <section class="friend-list" :aria-label="t('friends.listLabel', { tab: activeTabLabel })">
            <h2 class="friend-list-heading">
              <span>
                {{
                  activeTab === 'online'
                    ? t('friends.onlineCount', { count: visibleFriends.length })
                  : activeTab === 'pending'
                      ? t('friends.pendingCount', { count: visibleFriends.length })
                    : activeTab === 'blocked'
                      ? t('friends.blockedCount', { count: visibleFriends.length })
                    : t('friends.totalCount', { count: visibleFriends.length })
                }}
              </span>
              <button
                v-if="activeTab === 'all'"
                type="button"
                class="friend-sort-inline"
                :aria-label="sortDirection === 'asc' ? t('friends.sortAscending') : t('friends.sortDescending')"
                @click="toggleSortDirection"
              >
                <ArrowUpAZ v-if="sortDirection === 'asc'" :size="14" aria-hidden="true" />
                <ArrowDownAZ v-else :size="14" aria-hidden="true" />
                <span>{{ sortDirection === 'asc' ? t('friends.sortAscending') : t('friends.sortDescending') }}</span>
              </button>
            </h2>
            <div v-if="!visibleFriends.length" class="friends-empty">{{ emptyCopy }}</div>
            <section
              v-for="group in friendGroups"
              v-else
              :key="group.id"
              class="friend-request-group"
              :aria-label="group.label"
            >
              <h3
                v-if="(activeTab === 'all' && group.id === 'favorites') || (activeTab === 'pending' && friendGroups.length > 1)"
                class="friend-group-heading"
              >
                {{ group.label }}
              </h3>
              <article
                v-for="friend in group.friends"
                :key="friend.id"
                class="friend-row"
                :class="{
                  active: selectedFriend?.id === friend.id,
                  favorite: preferences.isFavoriteFriend(friend.id),
                }"
                data-context-kind="friend"
                :data-context-id="friend.id"
                :data-context-label="friend.username"
                @click="selectedFriendId = friend.id"
                @contextmenu.stop.prevent="openFriendMenu($event, friend, 'context')"
              >
                <span class="friend-avatar" aria-hidden="true">{{ friend.username.slice(0, 1).toUpperCase() }}</span>
                <span class="friend-copy">
                  <span class="friend-name-line">
                    <strong>{{ friend.username }}</strong>
                    <small>{{ friend.handle }}</small>
                    <small
                      v-if="preferences.isFavoriteFriend(friend.id)"
                      class="friend-favorite-label"
                    >
                      {{ t('friends.favoriteLabel') }}
                    </small>
                  </span>
                  <span class="friend-status-line">
                    <span class="presence-dot" :class="friend.status" aria-hidden="true"></span>
                    <small>{{ statusLabel(friend.status) }}</small>
                    <small v-if="friend.activity" class="friend-activity">{{ friend.activity }}</small>
                    <small v-if="friend.relationship !== 'friend'" class="friend-relationship">
                      {{ relationshipLabel(friend) }}
                    </small>
                  </span>
                </span>
                <span class="friend-actions" :aria-label="t('friends.more')">
                  <button
                    v-if="friend.relationship === 'friend'"
                    type="button"
                    class="friend-action-button"
                    :class="{ active: preferences.isFavoriteFriend(friend.id) }"
                    :aria-label="preferences.isFavoriteFriend(friend.id) ? t('friends.removeFavorite') : t('friends.addFavorite')"
                    :aria-pressed="preferences.isFavoriteFriend(friend.id)"
                    @click.stop="toggleFavorite(friend.id)"
                  >
                    <Star :size="17" aria-hidden="true" />
                  </button>
                  <button
                    v-if="friend.relationship === 'pending_incoming'"
                    type="button"
                    class="friend-action-button accept"
                    :aria-label="t('friends.acceptRequest')"
                    :disabled="props.disabled"
                    @click.stop="$emit('acceptFriend', friend.id)"
                  >
                    <Check :size="17" aria-hidden="true" />
                  </button>
                  <button
                    v-if="friend.relationship === 'pending_incoming'"
                    type="button"
                    class="friend-action-button danger"
                    :aria-label="t('friends.rejectRequest')"
                    :disabled="props.disabled"
                    @click.stop="$emit('rejectFriend', friend.id)"
                  >
                    <X :size="17" aria-hidden="true" />
                  </button>
                  <button
                    v-if="friend.relationship === 'pending_outgoing'"
                    type="button"
                    class="friend-action-button danger"
                    :aria-label="t('friends.cancelRequest')"
                    :disabled="props.disabled"
                    @click.stop="$emit('cancelFriend', friend.id)"
                  >
                    <X :size="17" aria-hidden="true" />
                  </button>
                  <button
                    v-if="friend.relationship === 'blocked'"
                    type="button"
                    class="friend-action-button accept"
                    :aria-label="t('friends.unblockUser')"
                    :disabled="props.disabled"
                    @click.stop="$emit('unblockFriend', friend.id)"
                  >
                    <UserRound :size="17" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    class="friend-action-button friend-menu-trigger"
                    :aria-label="t('friends.more')"
                    :aria-expanded="friendMenu?.friendId === friend.id"
                    @click.stop="openFriendMenu($event, friend, 'button')"
                  >
                    <MoreHorizontal :size="18" aria-hidden="true" />
                  </button>
                </span>
              </article>
            </section>
          </section>
        </div>

        <aside class="friend-activity-panel" :aria-label="t('friends.selectedProfile')">
          <h2>{{ t('friends.activityNow') }}</h2>
          <p v-if="!activeNowFriends.length" class="activity-empty">{{ t('friends.activityEmpty') }}</p>
          <article
            v-for="friend in activeNowFriends"
            :key="friend.id"
            class="activity-card selected"
            :class="{ active: selectedFriend?.id === friend.id }"
          >
            <span class="friend-avatar">
              {{ friend.username.slice(0, 1).toUpperCase() }}
            </span>
            <div>
              <strong>{{ friend.username }}</strong>
              <small class="friend-status-line">
                <span class="presence-dot" :class="friend.status" aria-hidden="true"></span>
                <span>{{ friend.activity || t('friends.noActivityOnline') }}</span>
              </small>
              <small>{{ friend.handle }}</small>
            </div>
            <button
              type="button"
              @click="$emit('messageFriend', friend.id)"
            >
              <Send :size="16" aria-hidden="true" />
              <span>{{ t('friends.sendMessage') }}</span>
            </button>
            <button
              type="button"
              @click="$emit('viewProfile', friend.id)"
            >
              <UserRound :size="16" aria-hidden="true" />
              <span>{{ t('friends.viewProfile') }}</span>
            </button>
          </article>
        </aside>
      </div>
    </template>

    <div
      v-if="friendMenu && openMenuFriend"
      class="friend-local-menu"
      :class="{ context: friendMenu.mode === 'context' }"
      :style="{ left: `${friendMenu.x}px`, top: `${friendMenu.y}px` }"
      role="menu"
      @click.stop
    >
      <header>
        <div>
          <strong>{{ openMenuFriend.username }}</strong>
          <small>{{ openMenuFriend.handle }}</small>
        </div>
        <button type="button" :aria-label="t('common.close')" @click="closeFriendMenu">
          <X :size="15" aria-hidden="true" />
        </button>
      </header>
      <button
        v-if="openMenuFriend.relationship === 'friend'"
        type="button"
        role="menuitem"
        @click="handleMenuAction('profile')"
      >
        <UserRound :size="15" aria-hidden="true" />
        <span>{{ t('friends.viewProfile') }}</span>
      </button>
      <button
        v-if="openMenuFriend.relationship === 'friend'"
        type="button"
        role="menuitem"
        @click="handleMenuAction('message')"
      >
        <Send :size="15" aria-hidden="true" />
        <span>{{ t('friends.sendMessage') }}</span>
      </button>
      <button
        v-if="openMenuFriend.relationship === 'friend'"
        type="button"
        role="menuitem"
        @click="handleMenuAction('call')"
      >
        <Phone :size="15" aria-hidden="true" />
        <span>{{ t('friends.startCall') }}</span>
      </button>
      <button
        v-if="openMenuFriend.relationship === 'friend'"
        type="button"
        role="menuitem"
        @click="handleMenuAction('mute')"
      >
        <BellOff :size="15" aria-hidden="true" />
        <span>{{ t('friends.muteConversation') }}</span>
      </button>
      <button
        v-if="openMenuFriend.relationship === 'friend'"
        type="button"
        role="menuitem"
        class="danger"
        @click="handleMenuAction('remove')"
      >
        <UserMinus :size="15" aria-hidden="true" />
        <span>{{ t('friends.removeFriend') }}</span>
      </button>
      <button
        v-if="openMenuFriend.relationship !== 'blocked'"
        type="button"
        role="menuitem"
        class="danger"
        @click="handleMenuAction('block')"
      >
        <UserX :size="15" aria-hidden="true" />
        <span>{{ t('friends.blockUser') }}</span>
      </button>
      <button
        v-else
        type="button"
        role="menuitem"
        @click="handleMenuAction('unblock')"
      >
        <UserRound :size="15" aria-hidden="true" />
        <span>{{ t('friends.unblockUser') }}</span>
      </button>
    </div>
  </section>
</template>
