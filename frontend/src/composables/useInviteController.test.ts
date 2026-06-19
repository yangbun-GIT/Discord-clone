import { describe, expect, it } from 'vitest'

import { useInviteController } from './useInviteController'
import type { Friend } from '../types'

const friends: Friend[] = [
  {
    id: 701,
    username: 'Mina',
    handle: 'mina.study',
    status: 'online',
    activity: null,
    relationship: 'friend',
  },
  {
    id: 702,
    username: 'Joon',
    handle: 'joon.dev',
    status: 'online',
    activity: null,
    relationship: 'friend',
  },
]

describe('useInviteController', () => {
  it('keeps invite code copy state separate from per-friend delivery state', () => {
    const controller = useInviteController(() => friends)

    controller.openInvite('abc123')
    controller.setInviteCodeCopied(true)
    controller.setInviteFriendState(701, 'sent')

    expect(controller.inviteCodeCopied.value).toBe(true)
    expect(controller.inviteFriendState(701)).toBe('sent')
    expect(controller.inviteFriendState(702)).toBe('idle')

    controller.closeInvite()

    expect(controller.inviteCodeCopied.value).toBe(false)
    expect(controller.inviteFriendState(701)).toBe('idle')
  })
})
