export type User = {
  id: number
  username: string
  status: number
}

export type Channel = {
  id: number
  guild_id: number
  name: string
  type: 0 | 1
  position: number
}

export type Member = {
  id: number
  username: string
  status: number
  role: string
  role_ids: number[]
}

export type Message = {
  id: number
  channel_id: number
  author_id: number
  author_name: string
  content: string
}

export type MessageDelete = {
  id: number
  channel_id: number
}

export type Role = {
  id: number
  guild_id: number
  name: string
  permissions: number
  position: number
}

export type Guild = {
  id: number
  name: string
  owner_id: number
  permissions: number
  channels: Channel[]
  roles: Role[]
  members: Member[]
  messages: Message[]
}

export type Invite = {
  code: string
  guild_id: number
  created_by: number
}

export type VoiceState = {
  guild_id: number
  channel_id: number | null
  user_id: number
  username: string | null
  self_mute: boolean
  self_deaf: boolean
}

export type VoiceSignal = {
  channel_id: number
  from_user_id: number
  from_username: string | null
  target_user_id: number
  type: 'offer' | 'answer' | 'ice'
  description?: Record<string, unknown> | null
  candidate?: Record<string, unknown> | null
}

export type VoiceIceServer = {
  urls: string | string[]
  username?: string
  credential?: string
}

export type VoiceConfig = {
  ice_servers: VoiceIceServer[]
}

export type RemoteVoiceStream = {
  userId: number
  username: string | null
  stream: MediaStream
  speaking: boolean
  sharingScreen: boolean
  connectionState: RTCPeerConnectionState
}
