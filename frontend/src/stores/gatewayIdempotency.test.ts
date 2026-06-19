import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useDmStore } from './dms'
import { useGuildStore } from './guilds'
import type { DirectMessage, Friend, Guild, Message } from '../types'

const guild: Guild = {
  id: 1001,
  name: 'Study Hall',
  owner_id: 42,
  permissions: 8,
  channels: [
    { id: 2001, guild_id: 1001, name: 'general', type: 0, position: 0 },
  ],
  roles: [],
  members: [],
  messages: [],
}

const serverMessage: Message = {
  id: 9101,
  channel_id: 2001,
  author_id: 42,
  author_name: 'yangbun',
  content: 'dedupe server message',
}

const dm: DirectMessage = {
  id: 801,
  recipient_ids: [701],
  participants: [
    {
      id: 42,
      username: 'yangbun',
      handle: 'yangbun',
      status: 'online',
      activity: null,
    },
    {
      id: 701,
      username: 'Mina',
      handle: 'mina.study',
      status: 'online',
      activity: null,
    },
  ],
  display_name: 'Mina',
  status: 'online',
  activity: null,
  unread_count: 0,
  is_group: false,
  member_count: 2,
  messages: [],
}

const dmMessage = {
  id: 9201,
  dm_id: 801,
  author_id: 701,
  author_name: 'Mina',
  content: 'dedupe dm message',
}

const relationship: Friend = {
  id: 701,
  username: 'Mina',
  handle: 'mina.study',
  status: 'idle',
  activity: 'Reviewing requests',
  relationship: 'friend',
}

describe('gateway dispatch idempotency', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('keeps one server message when REST reconciliation and gateway dispatch race', () => {
    const store = useGuildStore()
    store.guilds = [{ ...guild, messages: [serverMessage] }]

    store.handleGatewayDispatch('MESSAGE_CREATE', serverMessage)
    store.handleGatewayDispatch('MESSAGE_CREATE', serverMessage)

    expect(store.guilds[0].messages).toHaveLength(1)
    expect(store.guilds[0].messages[0]).toEqual(serverMessage)
  })

  it('keeps one DM message when REST reconciliation and gateway dispatch race', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)
    store.dms = [{ ...dm, messages: [dmMessage] }]
    store.setActiveDm(801)

    store.handleGatewayDispatch('DM_MESSAGE_CREATE', dmMessage)
    store.handleGatewayDispatch('DM_MESSAGE_CREATE', dmMessage)

    expect(store.dms[0].messages).toHaveLength(1)
    expect(store.dms[0].messages[0]).toEqual(dmMessage)
    expect(store.dms[0].unread_count).toBe(0)
  })

  it('increments unread count for inactive DM gateway messages', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)
    store.dms = [{ ...dm, messages: [] }]
    store.setActiveDm(null)

    store.handleGatewayDispatch('DM_MESSAGE_CREATE', dmMessage)

    expect(store.dms[0].messages).toHaveLength(1)
    expect(store.dms[0].unread_count).toBe(1)
  })

  it('clears unread count when a DM becomes active', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)
    store.dms = [{ ...dm, unread_count: 3, messages: [] }]

    store.setActiveDm(801)

    expect(store.dms[0].unread_count).toBe(0)
  })

  it('syncs relationship presence updates into existing DM rows', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)
    store.dms = [{ ...dm, participants: dm.participants.map((participant) => ({ ...participant })) }]

    store.handleGatewayDispatch('RELATIONSHIP_UPDATE', relationship)

    expect(store.relationships[0]).toMatchObject({
      id: 701,
      status: 'idle',
      activity: 'Reviewing requests',
    })
    expect(store.dms[0].status).toBe('idle')
    expect(store.dms[0].activity).toBe('Reviewing requests')
    expect(store.dms[0].participants.find((participant) => participant.id === 701)).toMatchObject({
      status: 'idle',
      activity: 'Reviewing requests',
    })
  })

  it('syncs lightweight presence updates into relationships and existing DM rows', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)
    store.relationships = [{ ...relationship, status: 'online', activity: null }]
    store.dms = [{ ...dm, participants: dm.participants.map((participant) => ({ ...participant })) }]

    store.handleGatewayDispatch('PRESENCE_UPDATE', {
      user_id: 701,
      username: 'Mina',
      status: 'dnd',
      activity: 'Focusing',
    })

    expect(store.relationships[0]).toMatchObject({
      id: 701,
      status: 'dnd',
      activity: 'Focusing',
    })
    expect(store.dms[0].status).toBe('dnd')
    expect(store.dms[0].activity).toBe('Focusing')
    expect(store.dms[0].participants.find((participant) => participant.id === 701)).toMatchObject({
      status: 'dnd',
      activity: 'Focusing',
    })
  })

  it('normalizes incoming DM_CREATE payloads to the current user perspective', () => {
    const store = useDmStore()
    store.setCurrentUserId(42)

    store.handleGatewayDispatch('DM_CREATE', {
      ...dm,
      recipient_ids: [42],
      display_name: 'yangbun',
      status: 'online',
      activity: null,
    })

    expect(store.dms[0]).toMatchObject({
      display_name: 'Mina',
      recipient_ids: [701],
      status: 'online',
    })
    expect(store.dms[0].messages).toEqual([])
  })

  it('replaces one voice state per guild user and removes leave events', () => {
    const store = useGuildStore()

    store.handleGatewayDispatch('VOICE_STATE_UPDATE', {
      guild_id: 1001,
      channel_id: 2003,
      user_id: 701,
      username: 'Mina',
      self_mute: false,
      self_deaf: false,
    })
    store.handleGatewayDispatch('VOICE_STATE_UPDATE', {
      guild_id: 1001,
      channel_id: 2003,
      user_id: 701,
      username: 'Mina',
      self_mute: true,
      self_deaf: false,
    })

    expect(store.voiceStates).toHaveLength(1)
    expect(store.voiceStates[0]).toMatchObject({
      guild_id: 1001,
      channel_id: 2003,
      user_id: 701,
      self_mute: true,
    })

    store.handleGatewayDispatch('VOICE_STATE_UPDATE', {
      guild_id: 1001,
      channel_id: null,
      user_id: 701,
      username: 'Mina',
      self_mute: false,
      self_deaf: false,
    })

    expect(store.voiceStates).toHaveLength(0)
  })

  it('replaces voice states from a channel-scoped snapshot', () => {
    const store = useGuildStore()

    store.handleGatewayDispatch('VOICE_STATE_UPDATE', {
      guild_id: 1001,
      channel_id: 2003,
      user_id: 701,
      username: 'Mina',
      self_mute: false,
      self_deaf: false,
    })
    store.handleGatewayDispatch('VOICE_STATE_SNAPSHOT', {
      guild_ids: [1001],
      channel_id: 2003,
      states: [
        {
          guild_id: 1001,
          channel_id: 2003,
          user_id: 702,
          username: 'Joon',
          self_mute: false,
          self_deaf: false,
        },
      ],
    })

    expect(store.voiceStates).toHaveLength(1)
    expect(store.voiceStates[0].user_id).toBe(702)
  })

  it('accepts screen-sharing voice signals from the gateway', () => {
    const store = useGuildStore()

    store.handleGatewayDispatch('VOICE_SIGNAL', {
      channel_id: 2003,
      from_user_id: 701,
      from_username: 'Mina',
      target_user_id: 42,
      type: 'screen',
      screen_sharing: false,
    })

    expect(store.lastVoiceSignal).toMatchObject({
      channel_id: 2003,
      from_user_id: 701,
      type: 'screen',
      screen_sharing: false,
    })
  })

  it('replaces gateway guild updates without duplicating guilds or losing valid active channel', () => {
    const store = useGuildStore()
    const updatedGuild: Guild = {
      ...guild,
      name: 'Study Hall Updated',
      channels: [
        ...guild.channels,
        { id: 2002, guild_id: 1001, name: 'planning', type: 0, position: 1 },
      ],
    }

    store.guilds = [{ ...guild }]
    store.activeGuildId = guild.id
    store.activeChannelId = 2001

    store.handleGatewayDispatch('GUILD_UPDATE', updatedGuild)
    store.handleGatewayDispatch('GUILD_UPDATE', updatedGuild)

    expect(store.guilds).toHaveLength(1)
    expect(store.guilds[0].name).toBe('Study Hall Updated')
    expect(store.guilds[0].channels).toHaveLength(2)
    expect(store.activeChannelId).toBe(2001)
  })
})
