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
