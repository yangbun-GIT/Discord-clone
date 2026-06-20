<script setup lang="ts">
import { computed, ref } from 'vue'
import { Hash, Search, Sparkles, Users, X } from 'lucide-vue-next'

import { useI18n } from '../i18n'

const emit = defineEmits<{
  close: []
  createServer: [name: string]
}>()

const { t } = useI18n()
const search = ref('')

const suggestedServers = computed(() => [
  {
    name: t('serverDiscovery.studyHall.name'),
    category: t('serverDiscovery.category.education'),
    members: t('serverDiscovery.members', { count: 128 }),
    channels: t('serverDiscovery.studyHall.channels'),
    accent: '#5eead4',
  },
  {
    name: t('serverDiscovery.projectLab.name'),
    category: t('serverDiscovery.category.collaboration'),
    members: t('serverDiscovery.members', { count: 84 }),
    channels: t('serverDiscovery.projectLab.channels'),
    accent: '#93c5fd',
  },
  {
    name: t('serverDiscovery.campusLounge.name'),
    category: t('serverDiscovery.category.community'),
    members: t('serverDiscovery.members', { count: 231 }),
    channels: t('serverDiscovery.campusLounge.channels'),
    accent: '#fca5a5',
  },
  {
    name: t('serverDiscovery.gameNight.name'),
    category: t('serverDiscovery.category.voice'),
    members: t('serverDiscovery.members', { count: 67 }),
    channels: t('serverDiscovery.gameNight.channels'),
    accent: '#c4b5fd',
  },
])

const filteredServers = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return suggestedServers.value
  return suggestedServers.value.filter((server) =>
    [server.name, server.category, server.channels].some((value) => value.toLowerCase().includes(query)),
  )
})
</script>

<template>
  <section
    class="modal-layer"
    :aria-label="t('serverDiscovery.aria')"
    @mousedown.self="$emit('close')"
    @click.self="$emit('close')"
  >
    <div class="server-discovery-dialog">
      <header class="server-add-header">
        <div>
          <div class="auth-mark">EX</div>
          <h2>{{ t('serverDiscovery.title') }}</h2>
        </div>
        <button type="button" :title="t('common.close')" :aria-label="t('common.close')" @click="$emit('close')">
          <X :size="18" aria-hidden="true" />
        </button>
      </header>

      <label class="discovery-search">
        <Search :size="17" aria-hidden="true" />
        <input
          v-model="search"
          type="search"
          :placeholder="t('serverDiscovery.searchPlaceholder')"
          :aria-label="t('serverDiscovery.searchPlaceholder')"
        />
      </label>

      <div class="discovery-server-grid" :aria-label="t('serverDiscovery.suggestions')">
        <article v-for="server in filteredServers" :key="server.name" class="discovery-server-card">
          <div class="discovery-server-mark" :style="{ background: server.accent }">
            {{ server.name.slice(0, 2).toUpperCase() }}
          </div>
          <div class="discovery-server-copy">
            <span>{{ server.category }}</span>
            <h3>{{ server.name }}</h3>
            <p><Hash :size="14" aria-hidden="true" />{{ server.channels }}</p>
            <p><Users :size="14" aria-hidden="true" />{{ server.members }}</p>
          </div>
          <button type="button" @click="$emit('createServer', server.name)">
            <Sparkles :size="16" aria-hidden="true" />
            <span>{{ t('serverDiscovery.create') }}</span>
          </button>
        </article>
      </div>
    </div>
  </section>
</template>
