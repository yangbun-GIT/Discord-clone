<script setup lang="ts">
import { Hash, LogOut, Radio, Trash2, UserPlus, Users, X } from 'lucide-vue-next'
import { computed } from 'vue'

import { useI18n } from '../i18n'
import type { Guild } from '../types'

const props = defineProps<{
  guild: Guild
  currentUserId: number | null
  loading: boolean
}>()

const emit = defineEmits<{
  close: []
  createInvite: []
  leaveGuild: []
  deleteGuild: []
}>()

const { t } = useI18n()
const isOwner = computed(() => props.currentUserId === props.guild.owner_id)
const canLeave = computed(() => props.currentUserId !== null && !isOwner.value)
const textChannelCount = computed(() => props.guild.channels.filter((channel) => channel.type === 0).length)
const voiceChannelCount = computed(() => props.guild.channels.filter((channel) => channel.type === 1).length)
const guildInitials = computed(() => props.guild.name.slice(0, 2).toUpperCase())
</script>

<template>
  <section class="modal-layer" :aria-label="t('serverSettings.title')" @click.self="$emit('close')">
    <div class="server-settings-dialog" role="dialog" :aria-label="t('serverSettings.title')" aria-modal="true">
      <header class="server-settings-header">
        <div class="server-settings-identity">
          <span class="server-settings-icon" aria-hidden="true">{{ guildInitials }}</span>
          <div>
            <h2>{{ guild.name }}</h2>
            <p>{{ t('serverSettings.subtitle') }}</p>
          </div>
        </div>
        <button type="button" :aria-label="t('common.close')" @click="$emit('close')">
          <X :size="18" aria-hidden="true" />
        </button>
      </header>

      <div class="server-settings-stats" aria-label="Server summary">
        <article>
          <Users :size="18" aria-hidden="true" />
          <span>{{ t('serverSettings.members', { count: guild.members.length }) }}</span>
        </article>
        <article>
          <Hash :size="18" aria-hidden="true" />
          <span>{{ t('serverSettings.textChannels', { count: textChannelCount }) }}</span>
        </article>
        <article>
          <Radio :size="18" aria-hidden="true" />
          <span>{{ t('serverSettings.voiceChannels', { count: voiceChannelCount }) }}</span>
        </article>
      </div>

      <div class="server-settings-actions">
        <button type="button" :disabled="loading" @click="$emit('createInvite')">
          <UserPlus :size="16" aria-hidden="true" />
          <span>{{ t('serverSettings.createInvite') }}</span>
        </button>
        <button v-if="canLeave" type="button" class="danger" :disabled="loading" @click="$emit('leaveGuild')">
          <LogOut :size="16" aria-hidden="true" />
          <span>{{ t('serverSettings.leaveServer') }}</span>
        </button>
        <button v-if="isOwner" type="button" class="danger" :disabled="loading" @click="$emit('deleteGuild')">
          <Trash2 :size="16" aria-hidden="true" />
          <span>{{ t('serverSettings.deleteServer') }}</span>
        </button>
      </div>

      <p v-if="isOwner" class="server-settings-note">{{ t('serverSettings.ownerNote') }}</p>
      <p v-else class="server-settings-note">{{ t('serverSettings.memberNote') }}</p>
    </div>
  </section>
</template>
