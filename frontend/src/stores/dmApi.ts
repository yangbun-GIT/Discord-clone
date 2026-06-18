import {
  createDirectMessage,
  createDirectMessageMessage,
  fetchDirectMessages,
  fetchRelationships,
} from '../services/api'
import type { DirectMessage, DmMessage, Friend } from '../types'

export async function loadDmWorkspace(token: string | null): Promise<{
  relationships: Friend[]
  directMessages: DirectMessage[]
}> {
  const [relationships, directMessages] = await Promise.all([
    fetchRelationships(token),
    fetchDirectMessages(token),
  ])
  return { relationships, directMessages }
}

export function loadDmRelationships(token: string | null): Promise<Friend[]> {
  return fetchRelationships(token)
}

export function loadDirectMessages(token: string | null): Promise<DirectMessage[]> {
  return fetchDirectMessages(token)
}

export function createDmChannel(
  token: string | null,
  recipientIds: number[],
): Promise<DirectMessage> | null {
  const uniqueRecipientIds = [...new Set(recipientIds)].filter((recipientId) => recipientId > 0)
  if (!uniqueRecipientIds.length) return null
  return createDirectMessage({ recipient_ids: uniqueRecipientIds }, token)
}

export function createDmChannelMessage(
  token: string | null,
  dmId: number,
  content: string,
): Promise<DmMessage> | null {
  const trimmedContent = content.trim()
  if (!trimmedContent) return null
  return createDirectMessageMessage(dmId, { dm_id: dmId, content: trimmedContent }, token)
}
