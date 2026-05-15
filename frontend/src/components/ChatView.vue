<script setup lang="ts">
import { Check, Pencil, Send, Trash2, X } from 'lucide-vue-next'
import { ref } from 'vue'

import type { Channel, Message, User } from '../types'

const props = defineProps<{
  channel: Channel | null
  messages: Message[]
  currentUser: User | null
  canManageMessages: boolean
}>()

const draft = ref('')
const editDraft = ref('')
const editingMessageId = ref<number | null>(null)

const emit = defineEmits<{
  send: [content: string]
  edit: [messageId: number, content: string]
  delete: [messageId: number]
}>()

function submitMessage() {
  const content = draft.value.trim()
  if (!content) return
  emit('send', content)
  draft.value = ''
}

function canEditMessage(message: Message) {
  return props.currentUser?.id === message.author_id
}

function canDeleteMessage(message: Message) {
  return canEditMessage(message) || props.canManageMessages
}

function startEdit(message: Message) {
  editingMessageId.value = message.id
  editDraft.value = message.content
}

function cancelEdit() {
  editingMessageId.value = null
  editDraft.value = ''
}

function submitEdit(message: Message) {
  const content = editDraft.value.trim()
  if (!content || content === message.content) {
    cancelEdit()
    return
  }
  emit('edit', message.id, content)
  cancelEdit()
}
</script>

<template>
  <section class="chat-view" aria-label="Messages">
    <div class="message-list">
      <article v-for="message in messages" :key="message.id" class="message-row">
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div class="message-main">
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>#{{ message.id }}</span>
            <div
              v-if="canEditMessage(message) || canDeleteMessage(message)"
              class="message-actions"
              aria-label="Message actions"
            >
              <button
                v-if="canEditMessage(message)"
                class="message-icon-button"
                type="button"
                title="Edit message"
                aria-label="Edit message"
                @click="startEdit(message)"
              >
                <Pencil :size="14" aria-hidden="true" />
              </button>
              <button
                v-if="canDeleteMessage(message)"
                class="message-icon-button danger"
                type="button"
                title="Delete message"
                aria-label="Delete message"
                @click="emit('delete', message.id)"
              >
                <Trash2 :size="14" aria-hidden="true" />
              </button>
            </div>
          </div>
          <form
            v-if="editingMessageId === message.id"
            class="message-edit-form"
            @submit.prevent="submitEdit(message)"
          >
            <input
              v-model="editDraft"
              aria-label="Edit message content"
              maxlength="2000"
              autofocus
              @keydown.esc.prevent="cancelEdit"
            />
            <button type="submit" title="Save message" :disabled="!editDraft.trim()">
              <Check :size="15" aria-hidden="true" />
            </button>
            <button type="button" title="Cancel edit" @click="cancelEdit">
              <X :size="15" aria-hidden="true" />
            </button>
          </form>
          <p v-else>{{ message.content }}</p>
        </div>
      </article>
    </div>

    <form class="composer" @submit.prevent="submitMessage">
      <input
        v-model="draft"
        :aria-label="`Message ${channel?.name ?? 'channel'}`"
        :placeholder="channel ? `Message #${channel.name}` : 'Loading channel'"
        maxlength="2000"
      />
      <button type="submit" title="Send message" :disabled="!draft.trim()">
        <Send :size="18" aria-hidden="true" />
      </button>
    </form>
  </section>
</template>
