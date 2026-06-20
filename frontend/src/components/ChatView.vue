<script setup lang="ts">
import {
  ArrowDown,
  Check,
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useI18n } from '../i18n'
import { addDocumentEventListener } from '../services/browserApi'
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
const activeComposerPanel = ref<'upload' | 'templates' | 'emoji' | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const messageList = ref<HTMLElement | null>(null)
const selectedFileLabel = ref('')
const showJumpToLatest = ref(false)
const { t } = useI18n()
let removeDocumentPointerDown: (() => void) | null = null
let removeDocumentKeyDown: (() => void) | null = null
const emojiOptions = ['😀', '😂', '👍', '🎉', '🔥', '💬', '✨', '🙌']
const replyTarget = computed(
  () => props.messages.find((message) => message.id === replyTargetId.value) ?? null,
)
const timelineDate = computed(() =>
  new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'long', day: 'numeric' }).format(
    new Date(2026, 4, 18),
  ),
)
const activeComposerPanelLabel = computed(() => {
  if (activeComposerPanel.value === 'upload') return t('chat.uploadFile')
  if (activeComposerPanel.value === 'templates') return t('chat.templates')
  if (activeComposerPanel.value === 'emoji') return t('chat.emoji')
  return ''
})

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
  activeComposerPanel.value = null
}

function isNearBottom() {
  const element = messageList.value
  if (!element) return true
  return element.scrollHeight - element.scrollTop - element.clientHeight < 96
}

function scrollToLatest(behavior: ScrollBehavior = 'auto') {
  const element = messageList.value
  if (!element) return
  element.scrollTo({ top: element.scrollHeight, behavior })
  showJumpToLatest.value = false
}

function handleMessageScroll() {
  showJumpToLatest.value = !isNearBottom()
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

function toggleComposerPanel(panel: 'upload' | 'templates' | 'emoji') {
  activeComposerPanel.value = activeComposerPanel.value === panel ? null : panel
}

function insertText(value: string) {
  draft.value = `${draft.value}${draft.value ? ' ' : ''}${value}`.slice(0, 2000)
}

function openFilePicker() {
  activeComposerPanel.value = 'upload'
  fileInput.value?.click()
}

function handleFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  selectedFileLabel.value = file ? `${file.name} - ${Math.ceil(file.size / 1024)} KB` : ''
}

function insertAppAction(action: 'poll' | 'todo') {
  insertText(action === 'poll' ? t('chat.templates.pollTemplate') : t('chat.templates.todoTemplate'))
  activeComposerPanel.value = null
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

function messageTime(index: number) {
  return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(
    new Date(2026, 4, 18, 8, 54 + index),
  )
}

function handleDocumentPointerDown(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (activeComposerPanel.value && !target.closest('.composer-shell')) {
    activeComposerPanel.value = null
  }
  if (optionsMessageId.value && !target.closest('.message-actions')) {
    optionsMessageId.value = null
  }
}

function handleDocumentKeyDown(event: KeyboardEvent) {
  if (event.key !== 'Escape') return
  activeComposerPanel.value = null
  optionsMessageId.value = null
}

onMounted(() => {
  removeDocumentPointerDown = addDocumentEventListener('mousedown', handleDocumentPointerDown)
  removeDocumentKeyDown = addDocumentEventListener('keydown', handleDocumentKeyDown)
  void nextTick(() => scrollToLatest())
})

onBeforeUnmount(() => {
  removeDocumentPointerDown?.()
  removeDocumentKeyDown?.()
  removeDocumentPointerDown = null
  removeDocumentKeyDown = null
})

watch(
  () => props.channel?.id,
  () => {
    draft.value = ''
    activeComposerPanel.value = null
    replyTargetId.value = null
    void nextTick(() => scrollToLatest())
  },
)

watch(
  () => props.messages.length,
  async () => {
    const shouldStick = !showJumpToLatest.value && isNearBottom()
    await nextTick()
    if (shouldStick) scrollToLatest()
  },
)
</script>

<template>
  <section class="chat-view" :aria-label="t('chat.aria.messages')">
    <div ref="messageList" class="message-list message-list-bottom" @scroll="handleMessageScroll">
      <div v-if="messages.length" class="date-divider"><span>{{ timelineDate }}</span></div>
      <article
        v-for="(message, index) in messages"
        :key="message.id"
        class="message-row"
        :class="{ 'options-open': optionsMessageId === message.id }"
        tabindex="0"
        data-context-kind="message"
        :data-context-label="message.author_name"
        @keydown.esc="optionsMessageId = null"
      >
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div class="message-main">
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>{{ messageTime(index) }}</span>
            <div
              class="message-actions"
              :aria-label="t('chat.aria.messageActions')"
            >
              <button
                class="message-icon-button"
                type="button"
                :title="t('chat.reply')"
                :aria-label="t('chat.reply')"
                @click="startReply(message)"
              >
                <Reply :size="14" aria-hidden="true" />
              </button>
              <button
                v-if="canEditMessage(message)"
                class="message-icon-button"
                type="button"
                :title="t('chat.editMessage')"
                :aria-label="t('chat.editMessage')"
                @click="startEdit(message)"
              >
                <Pencil :size="14" aria-hidden="true" />
              </button>
              <button
                v-if="canDeleteMessage(message)"
                class="message-icon-button danger"
                type="button"
                :title="t('chat.deleteMessage')"
                :aria-label="t('chat.deleteMessage')"
                @click="deleteMessage(message)"
              >
                <Trash2 :size="14" aria-hidden="true" />
              </button>
              <button
                class="message-icon-button"
                type="button"
                :title="t('chat.moreActions')"
                :aria-label="t('chat.moreActions')"
                :aria-expanded="optionsMessageId === message.id"
                @click="toggleOptions(message)"
              >
                <MoreHorizontal :size="15" aria-hidden="true" />
              </button>
              <div v-if="optionsMessageId === message.id" class="message-options-menu" role="menu">
                <button type="button" role="menuitem" @click="startReply(message)">
                  <Reply :size="14" aria-hidden="true" />
                  <span>{{ t('chat.reply') }}</span>
                </button>
                <button v-if="canEditMessage(message)" type="button" role="menuitem" @click="startEdit(message)">
                  <Pencil :size="14" aria-hidden="true" />
                  <span>{{ t('chat.edit') }}</span>
                </button>
                <button
                  v-if="canDeleteMessage(message)"
                  class="danger"
                  type="button"
                  role="menuitem"
                  @click="deleteMessage(message)"
                >
                  <Trash2 :size="14" aria-hidden="true" />
                  <span>{{ t('chat.delete') }}</span>
                </button>
              </div>
            </div>
          </div>
          <div v-if="replyTargetId === message.id" class="reply-preview" :aria-label="t('chat.aria.replyTarget')">
            {{ t('chat.replyingTo', { author: message.author_name }) }}
          </div>
          <form
            v-if="editingMessageId === message.id"
            class="message-edit-form"
            @submit.prevent="submitEdit(message)"
          >
            <input
              v-model="editDraft"
              :aria-label="t('chat.aria.editContent')"
              maxlength="2000"
              autofocus
              @keydown.esc.prevent="cancelEdit"
            />
            <button type="submit" :title="t('chat.saveMessage')" :disabled="!editDraft.trim()">
              <Check :size="15" aria-hidden="true" />
            </button>
            <button type="button" :title="t('chat.cancelEdit')" @click="cancelEdit">
              <X :size="15" aria-hidden="true" />
            </button>
          </form>
          <p v-else>{{ message.content }}</p>
        </div>
      </article>
      <div v-if="!messages.length" class="channel-empty-intro">
        <strong>{{ channel ? `#${channel.name}` : t('chat.loadingChannel') }}</strong>
        <span>{{ t('chat.emptyChannelHint') }}</span>
      </div>
    </div>

    <button
      v-if="showJumpToLatest"
      type="button"
      class="jump-to-latest"
      @click="scrollToLatest('smooth')"
    >
      <ArrowDown :size="15" aria-hidden="true" />
      <span>{{ t('chat.jumpToLatest') }}</span>
    </button>

    <section class="composer-shell" :aria-label="t('chat.aria.composer')">
      <div v-if="replyTarget" class="composer-reply-bar">
        <span>{{ t('chat.replyingTo', { author: replyTarget.author_name }) }}</span>
        <button type="button" :title="t('chat.cancelReply')" :aria-label="t('chat.cancelReply')" @click="cancelReply">
          <X :size="15" aria-hidden="true" />
        </button>
      </div>
      <form class="composer" @submit.prevent="submitMessage">
        <div class="composer-actions" :aria-label="t('chat.aria.composer')">
          <button
            type="button"
            :title="t('chat.uploadFile')"
            :aria-label="t('chat.uploadFile')"
            :aria-expanded="activeComposerPanel === 'upload'"
            @click="openFilePicker"
          >
            <PlusCircle :size="18" aria-hidden="true" />
          </button>
        </div>
        <input
          v-model="draft"
          :aria-label="t('chat.messageChannel', { channel: channel?.name ?? 'channel' })"
          :placeholder="channel ? t('chat.messageChannel', { channel: `#${channel.name}` }) : t('chat.loadingChannel')"
          maxlength="2000"
        />
        <div class="composer-actions composer-secondary-actions" :aria-label="t('chat.aria.expressionActions')">
          <button
            class="composer-optional-action"
            type="button"
            :title="t('chat.templates')"
            :aria-label="t('chat.templates')"
            :aria-expanded="activeComposerPanel === 'templates'"
            @click="toggleComposerPanel('templates')"
          >
            <ImagePlus :size="18" aria-hidden="true" />
          </button>
          <button
            type="button"
            :title="t('chat.emoji')"
            :aria-label="t('chat.emoji')"
            :aria-expanded="activeComposerPanel === 'emoji'"
            @click="toggleComposerPanel('emoji')"
          >
            <Laugh :size="18" aria-hidden="true" />
          </button>
        </div>
        <button class="composer-send-button" type="submit" :title="t('chat.sendMessage')" :disabled="!draft.trim()">
          <Send :size="18" aria-hidden="true" />
        </button>
      </form>
      <div v-if="activeComposerPanel" class="composer-demo-panel" role="status">
        <div class="composer-panel-copy">
          <strong>{{ t('chat.demoPanel.title', { label: activeComposerPanelLabel }) }}</strong>
          <span v-if="activeComposerPanel === 'upload'">
            {{ selectedFileLabel || t('chat.uploadDescription') }}
          </span>
          <span v-else-if="activeComposerPanel === 'templates'">{{ t('chat.templatesDescription') }}</span>
          <span v-else-if="activeComposerPanel === 'emoji'">{{ t('chat.emojiDescription') }}</span>
          <span v-else>{{ t('chat.demoPanel.description') }}</span>
        </div>
        <input ref="fileInput" class="visually-hidden" type="file" @change="handleFileSelected" />
        <div v-if="activeComposerPanel === 'emoji'" class="composer-emoji-grid">
          <button v-for="emoji in emojiOptions" :key="emoji" type="button" @click="insertText(emoji)">
            {{ emoji }}
          </button>
        </div>
        <div v-else-if="activeComposerPanel === 'templates'" class="composer-app-grid">
          <button type="button" @click="insertAppAction('poll')">{{ t('chat.templates.poll') }}</button>
          <button type="button" @click="insertAppAction('todo')">{{ t('chat.templates.todo') }}</button>
        </div>
        <button v-else-if="activeComposerPanel === 'upload'" type="button" @click="openFilePicker">
          {{ t('chat.chooseFile') }}
        </button>
        <button type="button" @click="activeComposerPanel = null">{{ t('common.close') }}</button>
      </div>
    </section>
  </section>
</template>
