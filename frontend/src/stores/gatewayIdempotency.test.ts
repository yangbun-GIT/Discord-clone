import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useDmStore } from './dms'
import { useGuildStore } from './guilds'
import type { DirectMessage, Guild, Message } from '../types'

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
    store.dms = [{ ...dm, messages: [dmMessage] }]

    store.handleGatewayDispatch('DM_MESSAGE_CREATE', dmMessage)
    store.handleGatewayDispatch('DM_MESSAGE_CREATE', dmMessage)

    expect(store.dms[0].messages).toHaveLength(1)
    expect(store.dms[0].messages[0]).toEqual(dmMessage)
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
