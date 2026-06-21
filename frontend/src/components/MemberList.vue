<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Circle, Plus, RefreshCw, Settings, UserMinus, X } from 'lucide-vue-next'

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
  createRole: [name: string, permissions: number]
  assignRole: [memberId: number, roleId: number]
  removeRole: [memberId: number, roleId: number]
  removeMember: [memberId: number]
  refresh: []
}>()

const ROLE_PRESETS = [
  { label: 'Label', value: 0 },
  { label: 'Moderator', value: (1 << 4) | (1 << 13) },
  { label: 'Voice', value: 1 << 24 },
  { label: 'Admin', value: 1 << 3 },
]

const roleName = ref('')
const rolePermissions = ref(0)
const showManagement = ref(false)
const selectedRoleByMember = reactive<Record<number, number | null>>({})
const roleOptions = computed(() => props.roles)
const { t } = useI18n()

function handleCreateRole() {
  const name = roleName.value.trim()
  if (!name) return
  emit('createRole', name, rolePermissions.value)
  roleName.value = ''
  rolePermissions.value = 0
}

function firstAssignableRole(member: Member) {
  return roleOptions.value.find((role) => !member.role_ids.includes(role.id))?.id ?? null
}

function assignableRoles(member: Member) {
  return roleOptions.value.filter((role) => !member.role_ids.includes(role.id))
}

function selectedAssignableRole(member: Member) {
  const selectedRoleId = selectedRoleByMember[member.id]
  if (selectedRoleId && assignableRoles(member).some((role) => role.id === selectedRoleId)) {
    return selectedRoleId
  }
  return firstAssignableRole(member)
}

function assignSelectedRole(member: Member) {
  const roleId = selectedAssignableRole(member)
  if (roleId === null) return
  emit('assignRole', member.id, roleId)
  selectedRoleByMember[member.id] = null
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
      <form class="role-create-form" @submit.prevent="handleCreateRole">
        <input
          v-model="roleName"
          autocomplete="off"
          maxlength="100"
          :placeholder="t('members.newRole')"
          :aria-label="t('members.newRole')"
          :disabled="disabled"
        />
        <select v-model.number="rolePermissions" :aria-label="t('members.permissionPreset')" :disabled="disabled">
          <option v-for="preset in ROLE_PRESETS" :key="preset.value" :value="preset.value">
            {{ preset.label }}
          </option>
        </select>
        <button type="submit" :aria-label="t('members.createRole')" :disabled="!roleName.trim() || disabled">
          <Plus :size="15" aria-hidden="true" />
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
      <div v-if="canManageRoles && showManagement && roles.length" class="member-role-controls">
        <div v-if="roles.some((item) => member.role_ids.includes(item.id))" class="member-role-chip-list">
          <button
            v-for="role in roles.filter((item) => member.role_ids.includes(item.id))"
            :key="role.id"
            type="button"
            class="role-chip"
            :aria-label="t('members.removeRole', { role: role.name, user: member.username })"
            :disabled="disabled"
            @click="emit('removeRole', member.id, role.id)"
          >
            <span>{{ role.name }}</span>
            <X :size="12" aria-hidden="true" />
          </button>
        </div>
        <form
          v-if="assignableRoles(member).length"
          class="member-role-assign-form"
          @submit.prevent="assignSelectedRole(member)"
        >
          <select
            v-model.number="selectedRoleByMember[member.id]"
            :aria-label="t('members.selectRole', { user: member.username })"
            :disabled="disabled"
          >
            <option
              v-for="role in assignableRoles(member)"
              :key="role.id"
              :value="role.id"
            >
              {{ role.name }}
            </option>
          </select>
          <button
            type="submit"
            class="role-add-button"
            :aria-label="t('members.assignSelectedRole', { user: member.username })"
            :disabled="disabled"
          >
            <Plus :size="13" aria-hidden="true" />
          </button>
        </form>
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
      <div v-else-if="showManagement && canRemoveMember(member)" class="member-role-controls">
        <button
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
