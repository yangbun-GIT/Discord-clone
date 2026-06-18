import { describe, expect, it } from 'vitest'

import {
  cleanVisibleGuild,
  cleanVisibleGuilds,
  isVisibleChannel,
  isVisibleGuildMessage,
} from './guildVisibility'
import type { Guild } from '../types'

const guild: Guild = {
  id: 1001,
  name: 'Study Hall',
  owner_id: 42,
  permissions: 8,
  channels: [
    { id: 2001, guild_id: 1001, name: 'general', type: 0, position: 0 },
    { id: 2002, guild_id: 1001, name: 'stage-13-smoke', type: 0, position: 1 },
  ],
  roles: [],
  members: [],
  messages: [
    {
      id: 3001,
      channel_id: 2001,
      author_id: 42,
      author_name: 'yangbun',
      content: 'visible message',
    },
    {
      id: 3002,
      channel_id: 2001,
      author_id: 43,
      author_name: 'QA Smoke',
      content: 'hidden author',
    },
    {
      id: 3003,
      channel_id: 2002,
      author_id: 42,
      author_name: 'yangbun',
      content: 'message in hidden channel',
    },
  ],
}

describe('guild visibility policy', () => {
  it('filters visual-test channels and their messages', () => {
    const cleanGuild = cleanVisibleGuild(guild)

    expect(cleanGuild?.channels.map((channel) => channel.name)).toEqual(['general'])
    expect(cleanGuild?.messages.map((message) => message.id)).toEqual([3001])
  })

  it('drops visual-test guilds', () => {
    expect(cleanVisibleGuilds([guild, { ...guild, id: 1002, name: 'test-server' }])).toHaveLength(1)
  })

  it('recognizes visible channel and message entries', () => {
    expect(isVisibleChannel(guild.channels[0])).toBe(true)
    expect(isVisibleChannel(guild.channels[1])).toBe(false)
    expect(isVisibleGuildMessage(guild.messages[0])).toBe(true)
    expect(isVisibleGuildMessage(guild.messages[1])).toBe(false)
  })
})
