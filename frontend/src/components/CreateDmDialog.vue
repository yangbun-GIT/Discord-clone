<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { MessageCircle, Search, X } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Friend } from '../types'

const props = defineProps<{
  open: boolean
  friends: Friend[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  close: []
  create: [recipientIds: number[]]
}>()

const { t } = useI18n()
const query = ref('')
const selectedIds = ref<number[]>([])

const availableFriends = computed(() =>
  props.friends.filter((friend) => friend.relationship === 'friend'),
)

const filteredFriends = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase()
  if (!normalizedQuery) return availableFriends.value
  return availableFriends.value.filter((friend) =>
    friend.username.toLowerCase().includes(normalizedQuery)
    || friend.handle.toLowerCase().includes(normalizedQuery),
  )
})

const selectedFriends = computed(() =>
  availableFriends.value.filter((friend) => selectedIds.value.includes(friend.id)),
)

function toggleRecipient(friendId: number) {
  selectedIds.value = selectedIds.value.includes(friendId)
    ? selectedIds.value.filter((id) => id !== friendId)
    : [...selectedIds.value, friendId]
}

function submitCreate() {
  if (!selectedIds.value.length || props.disabled) return
  emit('create', selectedIds.value)
}

watch(
  () => props.open,
  (open) => {
    if (open) return
    query.value = ''
    selectedIds.value = []
  },
)
</script>

<template>
  <div v-if="open" class="modal-backdrop" role="presentation" @mousedown.self="$emit('close')">
    <section class="app-dialog create-dm-dialog" role="dialog" aria-modal="true" :aria-label="t('dm.createTitle')">
      <header class="app-dialog-header">
        <div>
          <strong>{{ t('dm.createTitle') }}</strong>
          <span>{{ t('dm.createDescription') }}</span>
        </div>
        <button type="button" :aria-label="t('common.close')" @click="$emit('close')">
          <X :size="17" aria-hidden="true" />
        </button>
      </header>

      <label class="dialog-search">
        <Search :size="16" aria-hidden="true" />
        <input v-model="query" type="search" :placeholder="t('dm.createSearch')" autofocus />
      </label>

      <div v-if="selectedFriends.length" class="recipient-pills" :aria-label="t('dm.selectedRecipients')">
        <button
          v-for="friend in selectedFriends"
          :key="friend.id"
          type="button"
          @click="toggleRecipient(friend.id)"
        >
          {{ friend.username }}
          <X :size="13" aria-hidden="true" />
        </button>
      </div>

      <div class="recipient-list" role="listbox" :aria-label="t('dm.recipientList')">
        <button
          v-for="friend in filteredFriends"
          :key="friend.id"
          type="button"
          role="option"
          :aria-selected="selectedIds.includes(friend.id)"
          :class="{ selected: selectedIds.includes(friend.id) }"
          @click="toggleRecipient(friend.id)"
        >
          <span class="recipient-avatar">{{ friend.username.slice(0, 1).toUpperCase() }}</span>
          <span>
            <strong>{{ friend.username }}</strong>
            <small>{{ friend.handle }}</small>
          </span>
          <span class="presence-dot" :class="friend.status" aria-hidden="true"></span>
        </button>
        <p v-if="!filteredFriends.length" class="dialog-empty">{{ t('dm.createEmpty') }}</p>
      </div>

      <footer class="app-dialog-actions">
        <button type="button" @click="$emit('close')">{{ t('common.cancel') }}</button>
        <button
          type="button"
          class="primary"
          :disabled="disabled || !selectedIds.length"
          @click="submitCreate"
        >
          <MessageCircle :size="16" aria-hidden="true" />
          <span>{{ t('dm.createSubmit') }}</span>
        </button>
      </footer>
    </section>
  </div>
</template>
