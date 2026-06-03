<script setup lang="ts">
import {
  Check,
  Gift,
  ImagePlus,
  Laugh,
  MoreHorizontal,
  Pencil,
  PlusCircle,
  Reply,
  Send,
  Trash2,
  X,
} from 'lucide-vue-next'
import { computed, ref } from 'vue'

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
const replyTargetId = ref<number | null>(null)
const optionsMessageId = ref<number | null>(null)

const replyTarget = computed(
  () => props.messages.find((message) => message.id === replyTargetId.value) ?? null,
)

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
  replyTargetId.value = null
}

function canEditMessage(message: Message) {
  return props.currentUser?.id === message.author_id
}

function canDeleteMessage(message: Message) {
  return canEditMessage(message) || props.canManageMessages
}

function startEdit(message: Message) {
  optionsMessageId.value = null
  editingMessageId.value = message.id
  editDraft.value = message.content
}

function startReply(message: Message) {
  optionsMessageId.value = null
  replyTargetId.value = message.id
}

function cancelReply() {
  replyTargetId.value = null
}

function toggleOptions(message: Message) {
  optionsMessageId.value = optionsMessageId.value === message.id ? null : message.id
}

function deleteMessage(message: Message) {
  optionsMessageId.value = null
  emit('delete', message.id)
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
              class="message-actions"
              aria-label="Message actions"
            >
              <button
                class="message-icon-button"
                type="button"
                title="Reply"
                aria-label="Reply"
                @click="startReply(message)"
              >
                <Reply :size="14" aria-hidden="true" />
              </button>
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
                @click="deleteMessage(message)"
              >
                <Trash2 :size="14" aria-hidden="true" />
              </button>
              <button
                class="message-icon-button"
                type="button"
                title="More message actions"
                aria-label="More message actions"
                :aria-expanded="optionsMessageId === message.id"
                @click="toggleOptions(message)"
              >
                <MoreHorizontal :size="15" aria-hidden="true" />
              </button>
              <div v-if="optionsMessageId === message.id" class="message-options-menu" role="menu">
                <button type="button" role="menuitem" @click="startReply(message)">
                  <Reply :size="14" aria-hidden="true" />
                  <span>Reply</span>
                </button>
                <button v-if="canEditMessage(message)" type="button" role="menuitem" @click="startEdit(message)">
                  <Pencil :size="14" aria-hidden="true" />
                  <span>Edit</span>
                </button>
                <button
                  v-if="canDeleteMessage(message)"
                  class="danger"
                  type="button"
                  role="menuitem"
                  @click="deleteMessage(message)"
                >
                  <Trash2 :size="14" aria-hidden="true" />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          </div>
          <div v-if="replyTargetId === message.id" class="reply-preview" aria-label="Reply target">
            Replying to {{ message.author_name }}
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

    <section class="composer-shell" aria-label="Message composer">
      <div v-if="replyTarget" class="composer-reply-bar">
        <span>Replying to {{ replyTarget.author_name }}</span>
        <button type="button" title="Cancel reply" aria-label="Cancel reply" @click="cancelReply">
          <X :size="15" aria-hidden="true" />
        </button>
      </div>
      <form class="composer" @submit.prevent="submitMessage">
        <div class="composer-actions" aria-label="Composer actions">
          <button type="button" title="Upload file" aria-label="Upload file">
            <PlusCircle :size="18" aria-hidden="true" />
          </button>
          <button type="button" title="Send gift" aria-label="Send gift">
            <Gift :size="18" aria-hidden="true" />
          </button>
        </div>
        <input
          v-model="draft"
          :aria-label="`Message ${channel?.name ?? 'channel'}`"
          :placeholder="channel ? `Message #${channel.name}` : 'Loading channel'"
          maxlength="2000"
        />
        <div class="composer-actions" aria-label="Expression actions">
          <button type="button" title="Apps and actions" aria-label="Apps and actions">
            <ImagePlus :size="18" aria-hidden="true" />
          </button>
          <button type="button" title="Emoji" aria-label="Emoji">
            <Laugh :size="18" aria-hidden="true" />
          </button>
        </div>
        <button class="composer-send-button" type="submit" title="Send message" :disabled="!draft.trim()">
          <Send :size="18" aria-hidden="true" />
        </button>
      </form>
    </section>
  </section>
</template>
