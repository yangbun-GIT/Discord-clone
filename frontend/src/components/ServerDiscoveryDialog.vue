<script setup lang="ts">
import { computed, ref } from 'vue'
import { Hash, Search, Sparkles, Users, X } from 'lucide-vue-next'

const emit = defineEmits<{
  close: []
  createServer: [name: string]
}>()

const search = ref('')

const demoServers = [
  {
    name: 'Study Hall',
    category: 'Education',
    members: '128',
    channels: 'Q&A, lectures, exam prep',
    accent: '#5eead4',
  },
  {
    name: 'Project Lab',
    category: 'Collaboration',
    members: '84',
    channels: 'planning, code review, voice rooms',
    accent: '#93c5fd',
  },
  {
    name: 'Campus Lounge',
    category: 'Community',
    members: '231',
    channels: 'introductions, events, hangout',
    accent: '#fca5a5',
  },
  {
    name: 'Game Night',
    category: 'Voice',
    members: '67',
    channels: 'party finder, clips, voice queue',
    accent: '#c4b5fd',
  },
]

const filteredServers = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return demoServers
  return demoServers.filter((server) =>
    [server.name, server.category, server.channels].some((value) => value.toLowerCase().includes(query)),
  )
})
</script>

<template>
  <section class="modal-layer" aria-label="Server discovery">
    <div class="server-discovery-dialog">
      <header class="server-add-header">
        <div>
          <div class="auth-mark">EX</div>
          <h2>Explore Servers</h2>
        </div>
        <button type="button" title="Close" aria-label="Close" @click="$emit('close')">
          <X :size="18" aria-hidden="true" />
        </button>
      </header>

      <label class="discovery-search">
        <Search :size="17" aria-hidden="true" />
        <input v-model="search" type="search" placeholder="Search communities" aria-label="Search communities" />
      </label>

      <div class="discovery-server-grid" aria-label="Public demo servers">
        <article v-for="server in filteredServers" :key="server.name" class="discovery-server-card">
          <div class="discovery-server-mark" :style="{ background: server.accent }">
            {{ server.name.slice(0, 2).toUpperCase() }}
          </div>
          <div class="discovery-server-copy">
            <span>{{ server.category }}</span>
            <h3>{{ server.name }}</h3>
            <p><Hash :size="14" aria-hidden="true" />{{ server.channels }}</p>
            <p><Users :size="14" aria-hidden="true" />{{ server.members }} demo members</p>
          </div>
          <button type="button" @click="$emit('createServer', server.name)">
            <Sparkles :size="16" aria-hidden="true" />
            <span>Create</span>
          </button>
        </article>
      </div>
    </div>
  </section>
</template>
