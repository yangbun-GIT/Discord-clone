<script setup lang="ts">
import { Send } from 'lucide-vue-next'
import { ref, watch } from 'vue'

import { useI18n } from '../i18n'
import type { DirectMessage, User } from '../types'

const props = defineProps<{
  dm: DirectMessage | null
  currentUser: User | null
  disabled: boolean
}>()

const draft = ref('')
const { t } = useI18n()

const emit = defineEmits<{
  send: [content: string]
}>()

function submitMessage() {
  const content = draft.value.trim()
  if (!content || props.disabled || !props.dm) return
  emit('send', content)
  draft.value = ''
}

watch(
  () => props.dm?.id,
  () => {
    draft.value = ''
  },
)
</script>

<template>
  <section class="chat-view" :aria-label="t('dm.aria.directMessages')">
    <div class="message-list">
      <section v-if="dm" class="dm-chat-intro" :aria-label="t('dm.aria.conversation')">
        <div class="dm-placeholder-avatar" :class="dm.status">
          {{ dm.display_name.slice(0, 1).toUpperCase() }}
        </div>
        <h2>{{ dm.display_name }}</h2>
        <p v-if="dm.is_group">{{ t('dm.groupDescription', { count: dm.member_count }) }}</p>
        <p v-else>{{ dm.activity ?? t('dm.beginning') }}</p>
      </section>

      <section v-else class="dm-chat-intro" :aria-label="t('dm.aria.noSelection')">
        <div class="dm-placeholder-avatar">D</div>
        <h2>{{ t('app.status.directMessage') }}</h2>
        <p>{{ t('dm.selectConversation') }}</p>
      </section>

      <article v-for="message in dm?.messages ?? []" :key="message.id" class="message-row">
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div class="message-main">
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>#{{ message.id }}</span>
            <span v-if="currentUser?.id === message.author_id">{{ t('channel.you') }}</span>
          </div>
          <p>{{ message.content }}</p>
        </div>
      </article>
    </div>

    <form class="composer dm-composer" @submit.prevent="submitMessage">
      <input
        v-model="draft"
        :aria-label="t('dm.messageTarget', { target: dm?.display_name ?? t('app.status.directMessage') })"
        :placeholder="dm ? t('dm.messageTarget', { target: dm.display_name }) : t('dm.selectPlaceholder')"
        maxlength="2000"
        :disabled="disabled || !dm"
      />
      <button type="submit" :title="t('chat.sendMessage')" :disabled="disabled || !dm || !draft.trim()">
        <Send :size="18" aria-hidden="true" />
      </button>
    </form>
  </section>
</template>
