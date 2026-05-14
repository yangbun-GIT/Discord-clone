<script setup lang="ts">
import { Mic, PhoneOff, Radio } from 'lucide-vue-next'

import type { Channel } from '../types'

defineProps<{
  channel: Channel | null
  connected: boolean
}>()

defineEmits<{
  toggle: []
}>()
</script>

<template>
  <section class="voice-panel" aria-label="Voice controls">
    <div class="voice-copy">
      <Radio :size="17" aria-hidden="true" />
      <div>
        <span>{{ channel?.name ?? 'voice-room' }}</span>
        <small>{{ connected ? 'Connected' : 'Disconnected' }}</small>
      </div>
    </div>
    <button type="button" :title="connected ? 'Disconnect voice' : 'Connect voice'" @click="$emit('toggle')">
      <PhoneOff v-if="connected" :size="18" aria-hidden="true" />
      <Mic v-else :size="18" aria-hidden="true" />
    </button>
  </section>
</template>

