<script setup lang="ts">
import { Circle } from 'lucide-vue-next'

import type { Member } from '../types'

defineProps<{
  members: Member[]
}>()
</script>

<template>
  <aside class="member-list" aria-label="Members">
    <p>Members</p>
    <div v-for="member in members" :key="member.id" class="member-row">
      <span class="member-avatar">{{ member.username.slice(0, 1).toUpperCase() }}</span>
      <span class="member-name">{{ member.username }}</span>
      <Circle
        :size="10"
        :class="member.status === 1 ? 'online-dot' : 'offline-dot'"
        fill="currentColor"
        aria-hidden="true"
      />
    </div>
  </aside>
</template>

