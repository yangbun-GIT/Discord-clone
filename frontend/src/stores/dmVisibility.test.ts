import { describe, expect, it } from 'vitest'

import {
  cleanVisibleDirectMessage,
  cleanVisibleDirectMessages,
  cleanVisibleRelationships,
  isVisibleDmMessage,
} from './dmVisibility'
import type { DirectMessage, Friend } from '../types'

const friend: Friend = {
  id: 701,
  username: 'Mina',
  handle: 'mina.study',
  status: 'online',
  activity: 'Reading in voice',
  relationship: 'friend',
}

const dm: DirectMessage = {
  id: 9001,
  recipient_ids: [701],
  participants: [
    {
      id: 701,
      username: 'Mina',
      handle: 'mina.study',
      status: 'online',
      activity: 'Reading in voice',
    },
    {
      id: 702,
      username: 'Backend Pair',
      handle: 'backend.pair',
      status: 'online',
      activity: 'Checking API logs',
    },
  ],
  display_name: 'Mina',
  status: 'online',
  activity: null,
  unread_count: 0,
  is_group: false,
  member_count: 2,
  messages: [
    {
      id: 1,
      dm_id: 9001,
      author_id: 701,
      author_name: 'Mina',
      content: 'hello',
    },
    {
      id: 2,
      dm_id: 9001,
      author_id: 702,
      author_name: 'Backend Pair',
      content: 'Checking API logs',
    },
  ],
}

describe('dm visibility policy', () => {
  it('filters visual-test relationships', () => {
    expect(cleanVisibleRelationships([friend, { ...friend, username: 'QA Smoke' }])).toEqual([friend])
  })

  it('deduplicates relationships by user id', () => {
    expect(cleanVisibleRelationships([friend, { ...friend, status: 'idle' }])).toEqual([friend])
  })

  it('filters visual-test participants and messages inside a DM', () => {
    const cleanDm = cleanVisibleDirectMessage(dm)

    expect(cleanDm?.participants).toHaveLength(1)
    expect(cleanDm?.participants[0].username).toBe('Mina')
    expect(cleanDm?.messages).toHaveLength(1)
    expect(cleanDm?.messages[0].content).toBe('hello')
  })

  it('drops whole direct messages that are visual-test surfaces', () => {
    expect(cleanVisibleDirectMessages([dm, { ...dm, display_name: 'Stage 13 Smoke' }])).toHaveLength(1)
  })

  it('deduplicates one-to-one DMs by recipient set', () => {
    const cleanDm = cleanVisibleDirectMessage(dm)
    expect(cleanVisibleDirectMessages([
      dm,
      {
        ...dm,
        id: 9002,
        unread_count: 5,
      },
    ])).toEqual(cleanDm ? [cleanDm] : [])
  })

  it('recognizes visible and hidden messages', () => {
    expect(isVisibleDmMessage(dm.messages[0])).toBe(true)
    expect(isVisibleDmMessage(dm.messages[1])).toBe(false)
  })
})
