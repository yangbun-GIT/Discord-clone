<script setup lang="ts">
import { BellOff, MessageCircle, Phone, UserRound, X } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Friend } from '../types'

defineProps<{
  friend: Friend | null
  muted?: boolean
}>()

const emit = defineEmits<{
  close: []
  message: [friendId: number]
  call: [friendId: number]
  toggleMute: [friendId: number]
}>()

const { t } = useI18n()

function relationshipLabel(friend: Friend) {
  if (friend.relationship === 'pending_incoming') return t('friends.relationship.pending_incoming')
  if (friend.relationship === 'pending_outgoing') return t('friends.relationship.pending_outgoing')
  if (friend.relationship === 'blocked') return t('friends.relationship.blocked')
  return t('friends.relationship.friend')
}
</script>

<template>
  <div v-if="friend" class="modal-backdrop profile-backdrop" role="presentation" @mousedown.self="$emit('close')">
    <section class="app-dialog friend-profile-dialog" role="dialog" aria-modal="true" :aria-label="t('friends.viewProfile')">
      <header class="profile-banner">
        <button type="button" :aria-label="t('common.close')" @click="$emit('close')">
          <X :size="17" aria-hidden="true" />
        </button>
      </header>
      <div class="profile-body">
        <div class="profile-avatar" aria-hidden="true">{{ friend.username.slice(0, 1).toUpperCase() }}</div>
        <div class="profile-heading">
          <h2>{{ friend.username }}</h2>
          <span>{{ friend.handle }}</span>
          <small>
            <span class="presence-dot" :class="friend.status" aria-hidden="true"></span>
            {{ t(`common.status.${friend.status}`) }}
          </small>
        </div>
        <dl class="profile-summary-list">
          <div>
            <dt>{{ t('friends.relationship') }}</dt>
            <dd>{{ relationshipLabel(friend) }}</dd>
          </div>
          <div>
            <dt>{{ t('friends.currentActivity') }}</dt>
            <dd>{{ friend.activity || t('friends.noActivity') }}</dd>
          </div>
        </dl>
      </div>
      <footer class="profile-actions">
        <button
          v-if="friend.relationship === 'friend'"
          type="button"
          class="primary"
          @click="emit('message', friend.id)"
        >
          <MessageCircle :size="16" aria-hidden="true" />
          <span>{{ t('friends.sendMessage') }}</span>
        </button>
        <button
          v-if="friend.relationship === 'friend'"
          type="button"
          @click="emit('call', friend.id)"
        >
          <Phone :size="16" aria-hidden="true" />
          <span>{{ t('friends.startCall') }}</span>
        </button>
        <button
          v-if="friend.relationship === 'friend'"
          type="button"
          @click="emit('toggleMute', friend.id)"
        >
          <BellOff :size="16" aria-hidden="true" />
          <span>{{ muted ? t('friends.unmuteConversation') : t('friends.muteConversation') }}</span>
        </button>
        <button v-if="friend.relationship !== 'friend'" type="button" @click="$emit('close')">
          <UserRound :size="16" aria-hidden="true" />
          <span>{{ t('common.close') }}</span>
        </button>
      </footer>
    </section>
  </div>
</template>
