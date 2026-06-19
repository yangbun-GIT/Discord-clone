import type {
  Channel,
  Guild,
  Message,
  MessageDelete,
  VoiceSignal,
  VoiceState,
  VoiceStateSnapshot,
} from '../types'

interface GuildGatewayHandlerContext {
  appendMessage: (message: Message) => void
  updateMessage: (message: Message) => void
  deleteStoredMessage: (message: MessageDelete) => void
  appendChannel: (channel: Channel) => void
  syncVoiceState: (voiceState: VoiceState) => void
  syncVoiceSnapshot: (snapshot: VoiceStateSnapshot) => void
  syncGuildUpdate: (guild: Guild) => void
  setLastVoiceSignal: (signal: VoiceSignal) => void
}

type GuildGatewayHandler = (
  data: Record<string, unknown>,
  context: GuildGatewayHandlerContext,
) => void

function isMessage(data: Record<string, unknown>): data is Message {
  return typeof data.id === 'number'
    && typeof data.channel_id === 'number'
    && typeof data.author_id === 'number'
    && typeof data.author_name === 'string'
    && typeof data.content === 'string'
}

function isMessageDelete(data: Record<string, unknown>): data is MessageDelete {
  return typeof data.id === 'number' && typeof data.channel_id === 'number'
}

function isChannel(data: Record<string, unknown>): data is Channel {
  return typeof data.id === 'number'
    && typeof data.guild_id === 'number'
    && typeof data.name === 'string'
    && typeof data.type === 'number'
    && typeof data.position === 'number'
}

function isVoiceState(data: Record<string, unknown>): data is VoiceState {
  return typeof data.guild_id === 'number'
    && (data.channel_id === null || typeof data.channel_id === 'number')
    && typeof data.user_id === 'number'
    && typeof data.self_mute === 'boolean'
    && typeof data.self_deaf === 'boolean'
}

function isVoiceStateSnapshot(data: Record<string, unknown>): data is VoiceStateSnapshot {
  return Array.isArray(data.guild_ids)
    && data.guild_ids.every((guildId) => typeof guildId === 'number')
    && (data.channel_id === null || typeof data.channel_id === 'number')
    && Array.isArray(data.states)
    && data.states.every((state) => (
      state !== null
      && typeof state === 'object'
      && isVoiceState(state as Record<string, unknown>)
    ))
}

function isVoiceSignal(data: Record<string, unknown>): data is VoiceSignal {
  return typeof data.channel_id === 'number'
    && typeof data.from_user_id === 'number'
    && typeof data.target_user_id === 'number'
    && typeof data.type === 'string'
    && ['offer', 'answer', 'ice', 'screen'].includes(data.type)
}

function isGuild(data: Record<string, unknown>): data is Guild {
  return typeof data.id === 'number'
    && typeof data.name === 'string'
    && Array.isArray(data.channels)
    && Array.isArray(data.members)
    && Array.isArray(data.messages)
}

const handlers: Record<string, GuildGatewayHandler> = {
  MESSAGE_CREATE(data, context) {
    if (isMessage(data)) context.appendMessage(data)
  },
  MESSAGE_UPDATE(data, context) {
    if (isMessage(data)) context.updateMessage(data)
  },
  MESSAGE_DELETE(data, context) {
    if (isMessageDelete(data)) context.deleteStoredMessage(data)
  },
  CHANNEL_CREATE(data, context) {
    if (isChannel(data)) context.appendChannel(data)
  },
  VOICE_STATE_UPDATE(data, context) {
    if (isVoiceState(data)) context.syncVoiceState(data)
  },
  VOICE_STATE_SNAPSHOT(data, context) {
    if (isVoiceStateSnapshot(data)) context.syncVoiceSnapshot(data)
  },
  VOICE_SIGNAL(data, context) {
    if (isVoiceSignal(data)) context.setLastVoiceSignal(data)
  },
  GUILD_UPDATE(data, context) {
    if (isGuild(data)) context.syncGuildUpdate(data)
  },
}

export function handleGuildGatewayDispatch(
  event: string,
  data: Record<string, unknown>,
  context: GuildGatewayHandlerContext,
) {
  handlers[event]?.(data, context)
}
