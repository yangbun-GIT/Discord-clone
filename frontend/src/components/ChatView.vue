<script setup lang="ts">
import { Send } from 'lucide-vue-next'
import { ref } from 'vue'

import type { Channel, Message, User } from '../types'

defineProps<{
  channel: Channel | null
  messages: Message[]
  currentUser: User | null
}>()

const draft = ref('')

const emit = defineEmits<{
  send: [content: string]
}>()

function submitMessage() {
  const content = draft.value.trim()
  if (!content) return
  emit('send', content)
  draft.value = ''
}
</script>

<template>
  <section class="chat-view" aria-label="Messages">
    <div class="message-list">
      <article v-for="message in messages" :key="message.id" class="message-row">
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div>
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>#{{ message.id }}</span>
          </div>
          <p>{{ message.content }}</p>
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
