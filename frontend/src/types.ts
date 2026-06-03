export type User = {
  id: number
  username: string
  status: number
}

export type UserPresenceStatus = 'online' | 'idle' | 'dnd' | 'offline'

export type Friend = {
  id: number
  username: string
  handle: string
  status: UserPresenceStatus
  activity: string | null
  relationship: 'friend' | 'pending_incoming' | 'pending_outgoing' | 'blocked'
}

export type DirectMessage = {
  id: number
  recipient_ids: number[]
  participants: DmParticipant[]
  display_name: string
  status: UserPresenceStatus
  activity: string | null
  unread_count: number
  is_group: boolean
  member_count: number
  messages: DmMessage[]
}

export type DmParticipant = {
  id: number
  username: string
  handle: string
  status: UserPresenceStatus
  activity: string | null
}

export type DmMessage = {
  id: number
  dm_id: number
  author_id: number
  author_name: string
  content: string
}

export type DmCreate = {
  recipient_ids: number[]
}

export type DmMessageCreate = {
  dm_id: number
  content: string
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

export type ServerRailGuildMeta = {
  unread_count: number
  mention_count: number
  muted: boolean
  folder_name: string | null
  folder_color: string | null
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
  ice_server_count: number
  turn_configured: boolean
}

export type VoiceQualityStats = {
  peerCount: number
  connectedPeerCount: number
  averageRoundTripTimeMs: number | null
  inboundAudioPacketsLost: number
  inboundAudioJitterMs: number | null
  outboundAudioBitrateKbps: number | null
  outboundScreenBitrateKbps: number | null
}

export type RemoteVoiceStream = {
  userId: number
  username: string | null
  stream: MediaStream
  speaking: boolean
  sharingScreen: boolean
  connectionState: RTCPeerConnectionState
}

export type StoreItemType =
  | 'avatar_decoration'
  | 'profile_effect'
  | 'nameplate'
  | 'bundle'
  | 'orb_exclusive'

export type StoreOwnershipState =
  | 'not_owned'
  | 'owned'
  | 'partially_owned'
  | 'nitro_only'
  | 'unavailable'

export type StoreSortMode =
  | 'recently_added'
  | 'price_low_to_high'
  | 'price_high_to_low'
  | 'name'
  | 'owned_first'

export type StoreEquipSlot = 'avatar_decoration' | 'profile_effect' | 'nameplate'

export type StorePrice = {
  price_display: string
  orb_price: number | null
  nitro_discount_percent: number | null
  is_nitro_discounted: boolean
}

export type StorePreviewStyle = {
  accent_color: string
  secondary_color: string | null
  effect: string | null
  icon: string | null
}

export type StoreCollection = {
  id: number
  slug: string
  name: string
  description: string
  accent_color: string
  item_count: number
  featured: boolean
  starts_at: string | null
  ends_at: string | null
  position: number
}

export type StoreItemSummary = {
  id: number
  collection_id: number
  type: StoreItemType
  slug: string
  title: string
  description: string
  price: StorePrice
  ownership_state: StoreOwnershipState
  tags: string[]
  colors: string[]
  theme: string
  preview: StorePreviewStyle
  featured: boolean
  limited: boolean
  giftable: boolean
  bundle_item_ids: number[]
}

export type StoreFilters = {
  item_types: StoreItemType[]
  colors: string[]
  themes: string[]
  collections: StoreCollection[]
  sort_modes: StoreSortMode[]
}

export type StoreCatalog = {
  collections: StoreCollection[]
  featured: StoreItemSummary[]
  items: StoreItemSummary[]
  categories: StoreItemType[]
  filters: StoreFilters
  orb_balance: number
  is_nitro_member: boolean
}

export type StoreItemDetail = {
  item: StoreItemSummary
  related_items: StoreItemSummary[]
  included_items: StoreItemSummary[]
  can_purchase: boolean
  can_gift: boolean
  can_equip: boolean
}

export type StoreEquippedCosmetics = {
  avatar_decoration_item_id: number | null
  profile_effect_item_id: number | null
  nameplate_item_id: number | null
}

export type StoreInventory = {
  items: StoreItemSummary[]
  equipped: StoreEquippedCosmetics
  orb_balance: number
  is_nitro_member: boolean
}

export type StorePurchaseCreate = {
  item_id: number
  currency: 'cash' | 'orbs'
}

export type StoreGiftCreate = {
  item_id: number
  recipient_id: number
  card_style: string
  note: string | null
  emoji_style: string | null
}

export type StoreEquipCreate = {
  item_id: number | null
  slot: StoreEquipSlot
}

export type StoreMutation = {
  item: StoreItemSummary | null
  inventory: StoreInventory
  message: string
}
