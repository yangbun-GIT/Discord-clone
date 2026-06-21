<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Circle, RefreshCw, Settings, UserMinus } from 'lucide-vue-next'

import { useI18n } from '../i18n'
import type { Member, Role, UserPresenceStatus } from '../types'

const props = defineProps<{
  members: Member[]
  roles: Role[]
  canManageRoles: boolean
  ownerId: number
  currentUserId?: number | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  setPermissionLevel: [memberId: number, level: 'member' | 'admin']
  removeMember: [memberId: number]
  refresh: []
}>()

const ADMINISTRATOR_PERMISSION = 1 << 3
const showManagement = ref(false)
const selectedMemberId = ref<number | null>(null)
const selectedPermissionLevel = ref<'member' | 'admin'>('member')
const { t } = useI18n()

const adminRoleIds = computed(() => (
  props.roles
    .filter((role) => (role.permissions & ADMINISTRATOR_PERMISSION) === ADMINISTRATOR_PERMISSION)
    .map((role) => role.id)
))

const selectedMemberModel = computed<number | null>({
  get() {
    if (selectedMemberId.value && props.members.some((member) => member.id === selectedMemberId.value)) {
      return selectedMemberId.value
    }
    return props.members[0]?.id ?? null
  },
  set(value) {
    selectedMemberId.value = value
  },
})

const selectedMember = computed(() => (
  props.members.find((member) => member.id === selectedMemberModel.value) ?? null
))

function isAdminMember(member: Member) {
  if (member.id === props.ownerId) return true
  return member.role_ids.some((roleId) => adminRoleIds.value.includes(roleId))
}

function permissionLevelForMember(member: Member | null) {
  return member && isAdminMember(member) ? 'admin' : 'member'
}

watch(selectedMember, (member) => {
  selectedPermissionLevel.value = permissionLevelForMember(member)
}, { immediate: true })

function applySelectedPermission() {
  const memberId = selectedMemberModel.value
  if (memberId === null) return
  emit('setPermissionLevel', memberId, selectedPermissionLevel.value)
}

function canRemoveMember(member: Member) {
  return props.canManageRoles && member.id !== props.ownerId && member.id !== props.currentUserId
}

function memberPresence(member: Member): UserPresenceStatus {
  return member.presence_status ?? (member.status === 1 ? 'online' : 'offline')
}

function memberStatus(member: Member) {
  const status = memberPresence(member)
  return status === 'online'
    ? t('members.status.online')
    : t(`common.status.${status}`)
}
</script>

<template>
  <aside class="member-list" :aria-label="t('members.aria.list')">
    <div class="member-list-heading">
      <p>
        {{ t('members.heading') }}
        <span>{{ t('members.count', { count: members.length }) }}</span>
      </p>
      <span class="member-list-actions">
        <button
          v-if="canManageRoles"
          type="button"
          class="member-management-toggle"
          :aria-label="t('members.manage')"
          :aria-pressed="showManagement"
          @click="showManagement = !showManagement"
        >
          <Settings :size="14" aria-hidden="true" />
        </button>
      </span>
    </div>
    <section v-if="canManageRoles && showManagement" class="member-management-panel" :aria-label="t('members.manage')">
      <div class="member-management-toolbar">
        <span>{{ t('members.manage') }}</span>
        <button type="button" :aria-label="t('members.refresh')" :disabled="disabled" @click="emit('refresh')">
          <RefreshCw :size="14" aria-hidden="true" />
        </button>
      </div>
      <form
        v-if="members.length"
        class="member-permission-form"
        @submit.prevent="applySelectedPermission"
      >
        <select
          v-model.number="selectedMemberModel"
          :aria-label="t('members.selectMember')"
          :disabled="disabled"
        >
          <option v-for="member in members" :key="member.id" :value="member.id">
            {{ member.username }}
          </option>
        </select>
        <select
          v-model="selectedPermissionLevel"
          :aria-label="t('members.selectPermissionLevel')"
          :disabled="disabled || !selectedMember || selectedMember.id === ownerId"
        >
          <option value="member">{{ t('members.permission.member') }}</option>
          <option value="admin">{{ t('members.permission.admin') }}</option>
        </select>
        <button
          type="submit"
          :aria-label="t('members.applyPermission')"
          :disabled="disabled || selectedMemberModel === null || selectedMember?.id === ownerId"
        >
          {{ t('members.apply') }}
        </button>
      </form>
    </section>
    <div v-for="member in members" :key="member.id" class="member-row">
      <span class="member-avatar">
        {{ member.username.slice(0, 1).toUpperCase() }}
      </span>
      <span class="member-copy">
        <span class="member-name">{{ member.username }}</span>
        <span class="member-role">{{ member.role }}</span>
      </span>
      <Circle
        :size="10"
        :class="`member-presence-dot ${memberPresence(member)}`"
        fill="currentColor"
        :aria-label="memberStatus(member)"
      />
      <div v-if="canManageRoles && showManagement" class="member-role-controls">
        <span class="member-permission-badge">
          {{ member.id === ownerId ? t('members.permission.owner') : isAdminMember(member) ? t('members.permission.admin') : t('members.permission.member') }}
        </span>
        <button
          v-if="canRemoveMember(member)"
          type="button"
          class="member-remove-button"
          :aria-label="t('members.removeMember', { user: member.username })"
          :disabled="disabled"
          @click="emit('removeMember', member.id)"
        >
          <UserMinus :size="13" aria-hidden="true" />
        </button>
      </div>
    </div>
  </aside>
</template>
