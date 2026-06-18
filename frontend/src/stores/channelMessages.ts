import { apiDelete, apiPatch, apiPost } from '../services/api'
import type { Message, MessageDelete } from '../types'

export function sendChannelMessage(
  token: string | null,
  channelId: number,
  content: string,
) {
  return apiPost<Message, { channel_id: number; content: string }>(
    `/api/channels/${channelId}/messages`,
    { channel_id: channelId, content },
    token,
  )
}

export function editChannelMessage(
  token: string | null,
  channelId: number,
  messageId: number,
  content: string,
) {
  return apiPatch<Message, { content: string }>(
    `/api/channels/${channelId}/messages/${messageId}`,
    { content },
    token,
  )
}

export function deleteChannelMessage(
  token: string | null,
  channelId: number,
  messageId: number,
) {
  return apiDelete<MessageDelete>(
    `/api/channels/${channelId}/messages/${messageId}`,
    token,
  )
}
