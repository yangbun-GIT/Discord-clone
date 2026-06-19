import { describe, expect, it, vi } from 'vitest'

import {
  handleDmGatewayDispatch,
  isDirectMessagePayload,
  isDmMessagePayload,
  isRelationshipDeletePayload,
  isRelationshipPayload,
} from './dmGatewayHandlers'
import type { DirectMessage, DmMessage, Friend, RelationshipDelete } from '../types'

const dm: DirectMessage = {
  id: 9001,
  recipient_ids: [701],
  participants: [],
  display_name: 'Mina',
  status: 'online',
  activity: null,
  unread_count: 0,
  is_group: false,
  member_count: 2,
  messages: [],
}

const message: DmMessage = {
  id: 9101,
  dm_id: 9001,
  author_id: 701,
  author_name: 'Mina',
  content: 'hello',
}

const relationship: Friend = {
  id: 701,
  username: 'Mina',
  handle: 'mina.study',
  status: 'online',
  activity: null,
  relationship: 'pending_incoming',
}

const relationshipDelete: RelationshipDelete = {
  id: 701,
}

describe('dm gateway handlers', () => {
  it('validates direct-message payload shape', () => {
    expect(isDirectMessagePayload(dm)).toBe(true)
    expect(isDirectMessagePayload({ ...dm, messages: null })).toBe(false)
  })

  it('validates direct-message message payload shape', () => {
    expect(isDmMessagePayload(message)).toBe(true)
    expect(isDmMessagePayload({ ...message, dm_id: '9001' })).toBe(false)
  })

  it('validates relationship payload shapes', () => {
    expect(isRelationshipPayload(relationship)).toBe(true)
    expect(isRelationshipPayload({ ...relationship, relationship: 'unknown' })).toBe(false)
    expect(isRelationshipDeletePayload(relationshipDelete)).toBe(true)
    expect(isRelationshipDeletePayload({ id: '701' })).toBe(false)
  })

  it('dispatches valid DM events to focused callbacks', () => {
    const upsertDm = vi.fn()
    const appendMessage = vi.fn()
    const upsertRelationship = vi.fn()
    const removeRelationship = vi.fn()

    handleDmGatewayDispatch('DM_CREATE', dm, {
      upsertDm,
      appendMessage,
      upsertRelationship,
      removeRelationship,
    })
    handleDmGatewayDispatch('DM_MESSAGE_CREATE', message, {
      upsertDm,
      appendMessage,
      upsertRelationship,
      removeRelationship,
    })
    handleDmGatewayDispatch('RELATIONSHIP_UPDATE', relationship, {
      upsertDm,
      appendMessage,
      upsertRelationship,
      removeRelationship,
    })
    handleDmGatewayDispatch('RELATIONSHIP_DELETE', relationshipDelete, {
      upsertDm,
      appendMessage,
      upsertRelationship,
      removeRelationship,
    })

    expect(upsertDm).toHaveBeenCalledWith(dm)
    expect(appendMessage).toHaveBeenCalledWith(message.dm_id, message)
    expect(upsertRelationship).toHaveBeenCalledWith(relationship)
    expect(removeRelationship).toHaveBeenCalledWith(relationshipDelete)
  })

  it('ignores invalid or unknown events', () => {
    const upsertDm = vi.fn()
    const appendMessage = vi.fn()

    handleDmGatewayDispatch('DM_CREATE', { ...dm, display_name: null }, { upsertDm, appendMessage })
    handleDmGatewayDispatch('UNKNOWN_EVENT', message, { upsertDm, appendMessage })

    expect(upsertDm).not.toHaveBeenCalled()
    expect(appendMessage).not.toHaveBeenCalled()
  })
})
