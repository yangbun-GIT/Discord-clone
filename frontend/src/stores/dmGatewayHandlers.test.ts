import { describe, expect, it, vi } from 'vitest'

import { handleDmGatewayDispatch, isDirectMessagePayload, isDmMessagePayload } from './dmGatewayHandlers'
import type { DirectMessage, DmMessage } from '../types'

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

describe('dm gateway handlers', () => {
  it('validates direct-message payload shape', () => {
    expect(isDirectMessagePayload(dm)).toBe(true)
    expect(isDirectMessagePayload({ ...dm, messages: null })).toBe(false)
  })

  it('validates direct-message message payload shape', () => {
    expect(isDmMessagePayload(message)).toBe(true)
    expect(isDmMessagePayload({ ...message, dm_id: '9001' })).toBe(false)
  })

  it('dispatches valid DM events to focused callbacks', () => {
    const upsertDm = vi.fn()
    const appendMessage = vi.fn()

    handleDmGatewayDispatch('DM_CREATE', dm, { upsertDm, appendMessage })
    handleDmGatewayDispatch('DM_MESSAGE_CREATE', message, { upsertDm, appendMessage })

    expect(upsertDm).toHaveBeenCalledWith(dm)
    expect(appendMessage).toHaveBeenCalledWith(message.dm_id, message)
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
