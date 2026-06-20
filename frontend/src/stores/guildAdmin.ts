import { apiDelete, apiPost } from '../services/api'
import type { Channel, Guild, Invite } from '../types'

export function createGuildInvite(token: string | null, guildId: number) {
  return apiPost<Invite, Record<string, never>>(`/api/guilds/${guildId}/invites`, {}, token)
}

export function joinGuildInvite(token: string | null, code: string) {
  return apiPost<Guild, Record<string, never>>(
    `/api/guilds/invites/${encodeURIComponent(code)}/join`,
    {},
    token,
  )
}

export function createGuildChannel(
  token: string | null,
  guildId: number,
  payload: { name: string; type: 0 | 1 },
) {
  return apiPost<Channel, { name: string; type: 0 | 1 }>(
    `/api/guilds/${guildId}/channels`,
    payload,
    token,
  )
}

export function createGuildRole(
  token: string | null,
  guildId: number,
  payload: { name: string; permissions: number },
) {
  return apiPost<Guild, { name: string; permissions: number }>(
    `/api/guilds/${guildId}/roles`,
    payload,
    token,
  )
}

export function assignGuildRole(
  token: string | null,
  guildId: number,
  memberId: number,
  roleId: number,
) {
  return apiPost<Guild, { role_id: number }>(
    `/api/guilds/${guildId}/members/${memberId}/roles`,
    { role_id: roleId },
    token,
  )
}

export function removeGuildRole(
  token: string | null,
  guildId: number,
  memberId: number,
  roleId: number,
) {
  return apiDelete<Guild>(
    `/api/guilds/${guildId}/members/${memberId}/roles/${roleId}`,
    token,
  )
}

export function removeGuildMember(
  token: string | null,
  guildId: number,
  memberId: number,
) {
  return apiDelete<Guild>(
    `/api/guilds/${guildId}/members/${memberId}`,
    token,
  )
}

export function leaveGuildMembership(token: string | null, guildId: number) {
  return apiDelete<{ ok: boolean }>(`/api/guilds/${guildId}/leave`, token)
}

export function deleteGuildById(token: string | null, guildId: number) {
  return apiDelete<{ ok: boolean }>(`/api/guilds/${guildId}`, token)
}
