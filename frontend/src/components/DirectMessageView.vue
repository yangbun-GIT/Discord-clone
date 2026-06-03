<script setup lang="ts">
import { Send } from 'lucide-vue-next'
import { ref, watch } from 'vue'

import type { DirectMessage, User } from '../types'

const props = defineProps<{
  dm: DirectMessage | null
  currentUser: User | null
  disabled: boolean
}>()

const draft = ref('')

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
  <section class="chat-view" aria-label="Direct messages">
    <div class="message-list">
      <section v-if="dm" class="dm-chat-intro" aria-label="Conversation">
        <div class="dm-placeholder-avatar" :class="dm.status">
          {{ dm.display_name.slice(0, 1).toUpperCase() }}
        </div>
        <h2>{{ dm.display_name }}</h2>
        <p v-if="dm.is_group">{{ dm.member_count }} members in this demo group conversation.</p>
        <p v-else>{{ dm.activity ?? `This is the beginning of your direct message history.` }}</p>
      </section>

      <section v-else class="dm-chat-intro" aria-label="No direct message selected">
        <div class="dm-placeholder-avatar">D</div>
        <h2>Direct Message</h2>
        <p>Select a conversation from the private sidebar.</p>
      </section>

      <article v-for="message in dm?.messages ?? []" :key="message.id" class="message-row">
        <div class="avatar" aria-hidden="true">
          {{ message.author_name.slice(0, 1).toUpperCase() }}
        </div>
        <div class="message-main">
          <div class="message-meta">
            <strong>{{ message.author_name }}</strong>
            <span>#{{ message.id }}</span>
            <span v-if="currentUser?.id === message.author_id">You</span>
          </div>
          <p>{{ message.content }}</p>
        </div>
      </article>
    </div>

    <form class="composer dm-composer" @submit.prevent="submitMessage">
      <input
        v-model="draft"
        :aria-label="`Message ${dm?.display_name ?? 'direct message'}`"
        :placeholder="dm ? `Message ${dm.display_name}` : 'Select a conversation'"
        maxlength="2000"
        :disabled="disabled || !dm"
      />
      <button type="submit" title="Send message" :disabled="disabled || !dm || !draft.trim()">
        <Send :size="18" aria-hidden="true" />
      </button>
    </form>
  </section>
</template>
