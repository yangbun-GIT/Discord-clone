import type { Ref, ShallowRef } from 'vue'

import type {
  RemoteVoiceStream,
  VoiceIceServer,
  VoiceQualityStats,
  VoiceSignal,
  VoiceState,
} from '../types'
import type {
  VoiceConstraintSupport,
  VoiceDeviceList,
  VoiceDeviceSettings,
  VoiceMediaErrorCode,
} from './voiceMedia'

export type VoiceTransportKind = 'p2p-webrtc' | 'sfu-webrtc'

export type SendVoiceTransportSignal = (payload: {
  channel_id: number
  target_user_id: number
  type: 'offer' | 'answer' | 'ice' | 'screen'
  description?: Record<string, unknown> | null
  candidate?: Record<string, unknown> | null
  screen_sharing?: boolean | null
}) => void

export interface VoiceTransportConnectOptions {
  channelId: number
  currentUserId: number
  participants: VoiceState[]
  iceServers: VoiceIceServer[]
  sendSignal: SendVoiceTransportSignal
}

export interface VoiceTransportState {
  localStream: ShallowRef<MediaStream | null>
  screenStream: ShallowRef<MediaStream | null>
  remoteStreams: ShallowRef<RemoteVoiceStream[]>
  isCapturing: Ref<boolean>
  isMuted: Ref<boolean>
  isScreenSharing: Ref<boolean>
  localSpeaking: Ref<boolean>
  inputLevel: Ref<number>
  error: Ref<string | null>
  errorCode: Ref<VoiceMediaErrorCode | null>
  constraintSupport: Ref<VoiceConstraintSupport>
  voiceDeviceSettings: Ref<VoiceDeviceSettings>
  voiceDevices: Ref<VoiceDeviceList>
  qualityStats: Ref<VoiceQualityStats>
}

export interface VoiceTransport extends VoiceTransportState {
  kind: VoiceTransportKind
  connect: (options: VoiceTransportConnectOptions) => Promise<void>
  disconnect: () => void
  setMuted: (muted: boolean) => void
  toggleMute: () => void
  toggleScreenShare: () => Promise<void>
  syncParticipants: (participants: VoiceState[]) => Promise<void>
  handleSignal: (signal: VoiceSignal) => Promise<void>
  refreshVoiceDevices: () => Promise<void>
  updateVoiceDeviceSettings: (settings: Partial<VoiceDeviceSettings>) => void
}

export const P2P_VOICE_TRANSPORT_KIND: VoiceTransportKind = 'p2p-webrtc'
