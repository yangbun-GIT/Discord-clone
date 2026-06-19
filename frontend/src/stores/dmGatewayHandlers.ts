import type { DirectMessage, DmMessage, Friend, RelationshipDelete } from '../types'

interface DmGatewayHandlerContext {
  upsertDm: (dm: DirectMessage) => void
  appendMessage: (dmId: number, message: DmMessage) => void
  upsertRelationship?: (relationship: Friend) => void
  removeRelationship?: (relationship: RelationshipDelete) => void
}

type DmGatewayHandler = (
  data: Record<string, unknown>,
  context: DmGatewayHandlerContext,
) => void

export function isDirectMessagePayload(data: Record<string, unknown>): data is DirectMessage {
  return typeof data.id === 'number'
    && Array.isArray(data.recipient_ids)
    && Array.isArray(data.participants)
    && typeof data.display_name === 'string'
    && Array.isArray(data.messages)
}

export function isDmMessagePayload(data: Record<string, unknown>): data is DmMessage {
  return typeof data.id === 'number'
    && typeof data.dm_id === 'number'
    && typeof data.author_id === 'number'
    && typeof data.author_name === 'string'
    && typeof data.content === 'string'
}

export function isRelationshipPayload(data: Record<string, unknown>): data is Friend {
  return typeof data.id === 'number'
    && typeof data.username === 'string'
    && typeof data.handle === 'string'
    && typeof data.status === 'string'
    && ['online', 'idle', 'dnd', 'offline'].includes(data.status)
    && (
      data.activity === null
      || typeof data.activity === 'string'
      || typeof data.activity === 'undefined'
    )
    && typeof data.relationship === 'string'
    && ['friend', 'pending_incoming', 'pending_outgoing', 'blocked'].includes(data.relationship)
}

export function isRelationshipDeletePayload(
  data: Record<string, unknown>,
): data is RelationshipDelete {
  return typeof data.id === 'number'
}

const handlers: Record<string, DmGatewayHandler> = {
  DM_CREATE(data, context) {
    if (isDirectMessagePayload(data)) context.upsertDm(data)
  },
  DM_MESSAGE_CREATE(data, context) {
    if (isDmMessagePayload(data)) context.appendMessage(data.dm_id, data)
  },
  RELATIONSHIP_UPDATE(data, context) {
    if (isRelationshipPayload(data)) context.upsertRelationship?.(data)
  },
  RELATIONSHIP_DELETE(data, context) {
    if (isRelationshipDeletePayload(data)) context.removeRelationship?.(data)
  },
}

export function handleDmGatewayDispatch(
  event: string,
  data: Record<string, unknown>,
  context: DmGatewayHandlerContext,
) {
  handlers[event]?.(data, context)
}
