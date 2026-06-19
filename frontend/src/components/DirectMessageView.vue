<script setup lang="ts">
import { Laugh, Send } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

import { useI18n } from '../i18n'
import type { DirectMessage, User } from '../types'

const props = defineProps<{
  dm: DirectMessage | null
  currentUser: User | null
  disabled: boolean
}>()

const draft = ref('')
const showEmojiPanel = ref(false)
const { t } = useI18n()
const emojiOptions = ['😀', '😂', '👍', '🎉', '🔥', '💬', '✨', '🙌']

const emit = defineEmits<{
  send: [content: string]
}>()

function submitMessage() {
  const content = draft.value.trim()
  if (!content || props.disabled || !props.dm) return
  emit('send', content)
  draft.value = ''
  showEmojiPanel.value = false
}

function insertEmoji(emoji: string) {
  draft.value = `${draft.value}${draft.value ? ' ' : ''}${emoji}`.slice(0, 2000)
}

const otherParticipants = computed(() =>
  props.dm?.participants.filter((participant) => participant.id !== props.currentUser?.id) ?? [],
)

function messageTime(index: number) {
  return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(
    new Date(2026, 4, 18, 8, 54 + index),
  )
}

const timelineDate = computed(() =>
  new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'long', day: 'numeric' }).format(
    new Date(2026, 4, 18),
  ),
)

watch(
  () => props.dm?.id,
  () => {
    draft.value = ''
    showEmojiPanel.value = false
  },
)
</script>

<template>
  <section class="chat-view" :aria-label="t('dm.aria.directMessages')">
    <div class="message-list">
      <section v-if="dm" class="dm-chat-intro" :aria-label="t('dm.aria.conversation')">
        <div class="dm-intro-heading">
          <div class="dm-placeholder-avatar">
            {{ dm.display_name.slice(0, 1).toUpperCase() }}
          </div>
          <div class="dm-intro-title">
            <h2>{{ dm.display_name }}</h2>
            <p v-if="dm.is_group">{{ t('dm.groupDescription', { count: dm.member_count }) }}</p>
            <p v-else>{{ t('dm.beginning') }}</p>
          </div>
        </div>
        <div v-if="otherParticipants.length" class="dm-participant-strip" :aria-label="t('dm.participants')">
          <span v-for="participant in otherParticipants" :key="participant.id">
            {{ participant.username }}
          </span>
        </div>
      </section>

      <section v-else class="dm-chat-intro" :aria-label="t('dm.aria.noSelection')">
        <div class="dm-placeholder-avatar">D</div>
        <h2>{{ t('app.status.directMessage') }}</h2>
        <p>{{ t('dm.selectConversation') }}</p>
      </section>

      <div v-if="dm?.messages.length" class="date-divider dm-date-divider"><span>{{ timelineDate }}</span></div>

      <article
        v-for="(message, index) in dm?.messages ?? []"
        :key="message.id"
        class="message-row"
        tabindex="0"
        data-context-kind="dm-message"
        :data-context-label="message.author_name"
      >
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div class="message-main">
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>{{ messageTime(index) }}</span>
            <span v-if="currentUser?.id === message.author_id">{{ t('channel.you') }}</span>
          </div>
          <p>{{ message.content }}</p>
        </div>
      </article>
    </div>

    <section class="composer-shell" :aria-label="t('chat.aria.composer')">
      <form class="composer dm-composer" @submit.prevent="submitMessage">
        <input
          v-model="draft"
          :aria-label="t('dm.messageTarget', { target: dm?.display_name ?? t('app.status.directMessage') })"
          :placeholder="dm ? t('dm.messageTarget', { target: dm.display_name }) : t('dm.selectPlaceholder')"
          maxlength="2000"
          :disabled="disabled || !dm"
        />
        <div class="composer-actions composer-secondary-actions" :aria-label="t('chat.aria.expressionActions')">
          <button
            type="button"
            :title="t('chat.emoji')"
            :aria-label="t('chat.emoji')"
            :aria-expanded="showEmojiPanel"
            :disabled="disabled || !dm"
            @click="showEmojiPanel = !showEmojiPanel"
          >
            <Laugh :size="18" aria-hidden="true" />
          </button>
        </div>
        <button
          class="composer-send-button"
          type="submit"
          :title="t('chat.sendMessage')"
          :disabled="disabled || !dm || !draft.trim()"
        >
          <Send :size="18" aria-hidden="true" />
        </button>
      </form>
      <div v-if="showEmojiPanel" class="composer-demo-panel" role="status">
        <div class="composer-panel-copy">
          <strong>{{ t('chat.demoPanel.title', { label: t('chat.emoji') }) }}</strong>
          <span>{{ t('chat.emojiDescription') }}</span>
        </div>
        <div class="composer-emoji-grid">
          <button v-for="emoji in emojiOptions" :key="emoji" type="button" @click="insertEmoji(emoji)">
            {{ emoji }}
          </button>
        </div>
        <button type="button" @click="showEmojiPanel = false">{{ t('common.close') }}</button>
      </div>
    </section>
  </section>
</template>
