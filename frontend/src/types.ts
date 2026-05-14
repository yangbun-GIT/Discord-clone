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
}

export type Message = {
  id: number
  channel_id: number
  author_id: number
  author_name: string
  content: string
}

export type Guild = {
  id: number
  name: string
  owner_id: number
  permissions: number
  channels: Channel[]
  members: Member[]
  messages: Message[]
}

