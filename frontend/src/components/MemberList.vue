<script setup lang="ts">
import { computed, ref } from 'vue'
import { Circle, Plus, RefreshCw, UserMinus, X } from 'lucide-vue-next'

import type { Member, Role } from '../types'

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
const roleOptions = computed(() => props.roles)

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

function assignFirstRole(member: Member) {
  const roleId = firstAssignableRole(member)
  if (roleId === null) return
  emit('assignRole', member.id, roleId)
}

function canRemoveMember(member: Member) {
  return props.canManageRoles && member.id !== props.ownerId && member.id !== props.currentUserId
}
</script>

<template>
  <aside class="member-list" aria-label="Members">
    <div class="member-list-heading">
      <p>Members</p>
      <button type="button" aria-label="Refresh members" :disabled="disabled" @click="emit('refresh')">
        <RefreshCw :size="14" aria-hidden="true" />
      </button>
    </div>
    <form v-if="canManageRoles" class="role-create-form" @submit.prevent="handleCreateRole">
      <input
        v-model="roleName"
        autocomplete="off"
        maxlength="100"
        placeholder="New role"
        aria-label="New role name"
        :disabled="disabled"
      />
      <select v-model.number="rolePermissions" aria-label="Role permission preset" :disabled="disabled">
        <option v-for="preset in ROLE_PRESETS" :key="preset.value" :value="preset.value">
          {{ preset.label }}
        </option>
      </select>
      <button type="submit" aria-label="Create role" :disabled="!roleName.trim() || disabled">
        <Plus :size="15" aria-hidden="true" />
      </button>
    </form>
    <div v-for="member in members" :key="member.id" class="member-row">
      <span class="member-avatar">{{ member.username.slice(0, 1).toUpperCase() }}</span>
      <span class="member-copy">
        <span class="member-name">{{ member.username }}</span>
        <span class="member-role">{{ member.role }}</span>
      </span>
      <Circle
        :size="10"
        :class="member.status === 1 ? 'online-dot' : 'offline-dot'"
        fill="currentColor"
        aria-hidden="true"
      />
      <div v-if="canManageRoles && roles.length" class="member-role-controls">
        <button
          v-for="role in roles.filter((item) => member.role_ids.includes(item.id))"
          :key="role.id"
          type="button"
          class="role-chip"
          :aria-label="`Remove ${role.name} from ${member.username}`"
          :disabled="disabled"
          @click="emit('removeRole', member.id, role.id)"
        >
          <span>{{ role.name }}</span>
          <X :size="12" aria-hidden="true" />
        </button>
        <button
          v-if="firstAssignableRole(member)"
          type="button"
          class="role-add-button"
          :aria-label="`Assign role to ${member.username}`"
          :disabled="disabled"
          @click="assignFirstRole(member)"
        >
          <Plus :size="13" aria-hidden="true" />
        </button>
        <button
          v-if="canRemoveMember(member)"
          type="button"
          class="member-remove-button"
          :aria-label="`Remove ${member.username}`"
          :disabled="disabled"
          @click="emit('removeMember', member.id)"
        >
          <UserMinus :size="13" aria-hidden="true" />
        </button>
      </div>
      <div v-else-if="canRemoveMember(member)" class="member-role-controls">
        <button
          type="button"
          class="member-remove-button"
          :aria-label="`Remove ${member.username}`"
          :disabled="disabled"
          @click="emit('removeMember', member.id)"
        >
          <UserMinus :size="13" aria-hidden="true" />
        </button>
      </div>
    </div>
  </aside>
</template>
