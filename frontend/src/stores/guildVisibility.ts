import type { Channel, Guild, Message } from '../types'
import { isVisualTestMessage, isVisualTestName } from '../utils/visualNoise'

export function isVisibleChannel(channel: Channel) {
  return !isVisualTestName(channel.name)
}

export function isVisibleGuildMessage(message: Message) {
  return !isVisualTestMessage(message.content) && !isVisualTestName(message.author_name)
}

export function cleanVisibleGuild(guild: Guild): Guild | null {
  if (isVisualTestName(guild.name)) return null
  const visibleChannels = guild.channels.filter(isVisibleChannel)
  const visibleChannelIds = new Set(visibleChannels.map((channel) => channel.id))
  return {
    ...guild,
    channels: visibleChannels,
    messages: guild.messages.filter(
      (message) => visibleChannelIds.has(message.channel_id) && isVisibleGuildMessage(message),
    ),
  }
}

export function cleanVisibleGuilds(guilds: Guild[]) {
  return guilds.flatMap((guild) => {
    const cleanGuild = cleanVisibleGuild(guild)
    return cleanGuild ? [cleanGuild] : []
  })
}
