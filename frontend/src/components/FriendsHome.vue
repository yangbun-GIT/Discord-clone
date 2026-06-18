<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  BellOff,
  MoreHorizontal,
  Phone,
  Search,
  Send,
  UserRound,
  UserX,
  X,
} from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Friend, UserPresenceStatus } from '../types'

const props = defineProps<{
  friends: Friend[]
}>()

const emit = defineEmits<{
  messageFriend: [friendId: number]
}>()

const activeTab = ref<'online' | 'all' | 'pending' | 'blocked' | 'add'>('online')
const searchQuery = ref('')
const addFriendName = ref('')
const addFriendResult = ref('')
const selectedFriendId = ref<number | null>(null)
const friendMenu = ref<{
  friendId: number
  mode: 'button' | 'context'
  x: number
  y: number
} | null>(null)
const { t } = useI18n()

const visualFallbackFriends: Friend[] = [
  {
    id: 701,
    username: 'Mina',
    handle: 'mina.study',
    status: 'online',
    activity: 'Reading in voice',
    relationship: 'friend',
  },
  {
    id: 702,
    username: 'Joon',
    handle: 'joon.dev',
    status: 'online',
    activity: 'Working on layout',
    relationship: 'friend',
  },
  {
    id: 703,
    username: 'Rina',
    handle: 'rina.notes',
    status: 'idle',
    activity: 'Reviewing notes',
    relationship: 'friend',
  },
  {
    id: 704,
    username: 'Haru',
    handle: 'haru.music',
    status: 'offline',
    activity: null,
    relationship: 'friend',
  },
  {
    id: 705,
    username: 'Nora',
    handle: 'nora.design',
    status: 'offline',
    activity: null,
    relationship: 'pending_incoming',
  },
]

const visualFriends = computed(() => (props.friends.length ? props.friends : visualFallbackFriends))

const visibleFriends = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return visualFriends.value.filter((friend) => {
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

function submitAddFriend() {
  const handle = addFriendName.value.trim()
  if (!handle) return
  addFriendResult.value = t('friends.addResult', { handle })
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

function handleMenuAction(action: 'message' | 'local') {
  if (action === 'message' && openMenuFriend.value) {
    emit('messageFriend', openMenuFriend.value.id)
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
  document.addEventListener('mousedown', handleDocumentPointerDown)
  document.addEventListener('keydown', handleDocumentKeyDown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentPointerDown)
  document.removeEventListener('keydown', handleDocumentKeyDown)
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
</script>

<template>
  <section class="friends-home" :aria-label="t('friends.title')">
    <header class="friends-header">
      <h1>{{ t('friends.title') }}</h1>
      <div class="friends-tabs" role="tablist" :aria-label="t('friends.title')">
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
          :aria-selected="activeTab === 'online'"
          :class="{ active: activeTab === 'online' }"
          @click="activeTab = 'online'"
        >
          {{ t('friends.online') }}
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
          class="add-tab"
          :aria-selected="activeTab === 'add'"
          :class="{ active: activeTab === 'add' }"
          @click="activeTab = 'add'"
        >
          {{ t('friends.add') }}
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
          <button type="submit" :disabled="!addFriendName.trim()">
            {{ t('friends.addSubmit') }}
          </button>
        </form>
        <p v-if="addFriendResult" class="add-friend-result" role="status">{{ addFriendResult }}</p>
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
              @contextmenu.prevent="openFriendMenu($event, friend, 'context')"
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
                  <small v-if="friend.relationship !== 'friend'" class="friend-relationship">
                    {{ relationshipLabel(friend) }}
                  </small>
                </span>
                <small v-if="friend.activity" class="friend-activity">{{ friend.activity }}</small>
              </span>
              <button
                type="button"
                class="friend-action-button"
                :aria-label="t('friends.sendMessage')"
                @click.stop="$emit('messageFriend', friend.id)"
              >
                <Send :size="17" aria-hidden="true" />
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
            </article>
          </section>
        </div>

        <aside v-if="selectedFriend" class="friend-activity-panel" :aria-label="t('friends.selectedProfile')">
          <h2>{{ t('friends.activityNow') }}</h2>
          <article class="activity-card selected">
            <span class="friend-avatar" :class="selectedFriend.status">
              {{ selectedFriend.username.slice(0, 1).toUpperCase() }}
            </span>
            <div>
              <strong>{{ selectedFriend.username }}</strong>
              <small>{{ selectedFriend.activity ?? statusLabel(selectedFriend.status) }}</small>
              <small>{{ selectedFriend.handle }}</small>
            </div>
            <button type="button" @click="$emit('messageFriend', selectedFriend.id)">
              <Send :size="16" aria-hidden="true" />
              <span>{{ t('friends.sendMessage') }}</span>
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
      <button type="button" role="menuitem" @click="handleMenuAction('message')">
        <Send :size="15" aria-hidden="true" />
        <span>{{ t('friends.sendMessage') }}</span>
      </button>
      <button type="button" role="menuitem" @click="handleMenuAction('local')">
        <Phone :size="15" aria-hidden="true" />
        <span>{{ t('friends.startCall') }}</span>
      </button>
      <button type="button" role="menuitem" @click="handleMenuAction('local')">
        <UserRound :size="15" aria-hidden="true" />
        <span>{{ t('friends.viewProfile') }}</span>
      </button>
      <button type="button" role="menuitem" @click="handleMenuAction('local')">
        <BellOff :size="15" aria-hidden="true" />
        <span>{{ t('friends.muteConversation') }}</span>
      </button>
      <button type="button" role="menuitem" class="danger" @click="handleMenuAction('local')">
        <UserX :size="15" aria-hidden="true" />
        <span>{{ t('friends.blockUser') }}</span>
      </button>
    </div>
  </section>
</template>
