import type { ShallowRef } from 'vue'

import type { RemoteVoiceStream, VoiceIceServer, VoiceSignal, VoiceState } from '../types'
import { screenTrackIsActive } from './voiceMedia'

export type SendVoiceSignal = (payload: {
  channel_id: number
  target_user_id: number
  type: 'offer' | 'answer' | 'ice'
  description?: Record<string, unknown> | null
  candidate?: Record<string, unknown> | null
}) => void

export type ConnectOptions = {
  channelId: number
  currentUserId: number
  participants: VoiceState[]
  iceServers: VoiceIceServer[]
  sendSignal: SendVoiceSignal
}

export type PeerEntry = {
  connection: RTCPeerConnection
  username: string | null
  stream: MediaStream
  screenSender: RTCRtpSender | null
}

interface VoicePeerRegistryOptions {
  remoteStreams: ShallowRef<RemoteVoiceStream[]>
  getActiveOptions: () => ConnectOptions | null
  getLocalStream: () => MediaStream | null
  getScreenStream: () => MediaStream | null
}

function toDescription(description: Record<string, unknown>) {
  return new RTCSessionDescription(description as unknown as RTCSessionDescriptionInit)
}

function toIceCandidate(candidate: Record<string, unknown>) {
  return new RTCIceCandidate(candidate as RTCIceCandidateInit)
}

function participantPeers(participants: VoiceState[], currentUserId: number) {
  return participants.filter(
    (participant) =>
      participant.channel_id !== null
      && participant.user_id !== currentUserId,
  )
}

export function createVoicePeerRegistry(options: VoicePeerRegistryOptions) {
  const peers = new Map<number, PeerEntry>()

  function replaceRemoteStream(userId: number, patch: Partial<RemoteVoiceStream>) {
    options.remoteStreams.value = options.remoteStreams.value.map((remote) =>
      remote.userId === userId ? { ...remote, ...patch } : remote,
    )
  }

  function removeRemoteStream(userId: number) {
    options.remoteStreams.value = options.remoteStreams.value.filter((remote) => remote.userId !== userId)
  }

  function ensurePeer(userId: number, username: string | null) {
    const activeOptions = options.getActiveOptions()
    const localStream = options.getLocalStream()
    if (!activeOptions || !localStream) {
      throw new Error('voice is not connected')
    }
    const existing = peers.get(userId)
    if (existing) return existing

    const stream = new MediaStream()
    const connection = new RTCPeerConnection({ iceServers: activeOptions.iceServers })
    localStream.getTracks().forEach((track) => {
      connection.addTrack(track, localStream)
    })

    const screenStream = options.getScreenStream()
    const screenTrack = screenStream?.getVideoTracks()[0]
    let screenSender: RTCRtpSender | null = null
    if (screenTrack && screenTrack.readyState === 'live' && screenStream) {
      screenSender = connection.addTrack(screenTrack, screenStream)
    }

    connection.addEventListener('icecandidate', (event) => {
      const currentOptions = options.getActiveOptions()
      if (!event.candidate || !currentOptions) return
      currentOptions.sendSignal({
        channel_id: currentOptions.channelId,
        target_user_id: userId,
        type: 'ice',
        candidate: event.candidate.toJSON() as Record<string, unknown>,
      })
    })
    connection.addEventListener('track', (event) => {
      stream.addTrack(event.track)
      const current = options.remoteStreams.value.find((remote) => remote.userId === userId)
      const sharingScreen = screenTrackIsActive(stream)
      if (current) {
        replaceRemoteStream(userId, { stream, sharingScreen })
        return
      }
      options.remoteStreams.value = [
        ...options.remoteStreams.value,
        {
          userId,
          username,
          stream,
          speaking: false,
          sharingScreen,
          connectionState: connection.connectionState,
        },
      ]
    })
    connection.addEventListener('connectionstatechange', () => {
      replaceRemoteStream(userId, { connectionState: connection.connectionState })
      if (['closed', 'disconnected', 'failed'].includes(connection.connectionState)) {
        removeRemoteStream(userId)
      }
    })

    const entry = { connection, username, stream, screenSender }
    peers.set(userId, entry)
    return entry
  }

  async function createOfferFor(userId: number, username: string | null) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions) return
    const peer = ensurePeer(userId, username)
    if (peer.connection.signalingState !== 'stable') return
    const offer = await peer.connection.createOffer()
    await peer.connection.setLocalDescription(offer)
    activeOptions.sendSignal({
      channel_id: activeOptions.channelId,
      target_user_id: userId,
      type: 'offer',
      description: { type: offer.type, sdp: offer.sdp ?? '' },
    })
  }

  async function renegotiatePeer(userId: number, peer: PeerEntry) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || peer.connection.signalingState !== 'stable') return
    const offer = await peer.connection.createOffer()
    await peer.connection.setLocalDescription(offer)
    activeOptions.sendSignal({
      channel_id: activeOptions.channelId,
      target_user_id: userId,
      type: 'offer',
      description: { type: offer.type, sdp: offer.sdp ?? '' },
    })
  }

  async function renegotiateAllPeers() {
    await Promise.all(
      [...peers.entries()].map(([userId, peer]) => renegotiatePeer(userId, peer)),
    )
  }

  async function syncParticipants(participants: VoiceState[]) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || !options.getLocalStream()) return
    const activePeerIds = new Set(
      participantPeers(participants, activeOptions.currentUserId).map((participant) => participant.user_id),
    )
    for (const [userId, peer] of peers) {
      if (activePeerIds.has(userId)) continue
      peer.connection.close()
      peers.delete(userId)
      removeRemoteStream(userId)
    }
    for (const participant of participantPeers(participants, activeOptions.currentUserId)) {
      if (activeOptions.currentUserId < participant.user_id) {
        await createOfferFor(participant.user_id, participant.username)
      }
    }
  }

  async function handleSignal(signal: VoiceSignal) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || signal.target_user_id !== activeOptions.currentUserId) return
    const peer = ensurePeer(signal.from_user_id, signal.from_username)
    if (signal.type === 'offer' && signal.description) {
      await peer.connection.setRemoteDescription(toDescription(signal.description))
      const answer = await peer.connection.createAnswer()
      await peer.connection.setLocalDescription(answer)
      activeOptions.sendSignal({
        channel_id: activeOptions.channelId,
        target_user_id: signal.from_user_id,
        type: 'answer',
        description: { type: answer.type, sdp: answer.sdp ?? '' },
      })
      return
    }
    if (signal.type === 'answer' && signal.description) {
      await peer.connection.setRemoteDescription(toDescription(signal.description))
      return
    }
    if (signal.type === 'ice' && signal.candidate) {
      await peer.connection.addIceCandidate(toIceCandidate(signal.candidate))
    }
  }

  function closeAll() {
    peers.forEach((peer) => {
      peer.connection.close()
      peer.stream.getTracks().forEach((track) => track.stop())
    })
    peers.clear()
    options.remoteStreams.value = []
  }

  return {
    peers,
    closeAll,
    renegotiateAllPeers,
    syncParticipants,
    handleSignal,
  }
}
