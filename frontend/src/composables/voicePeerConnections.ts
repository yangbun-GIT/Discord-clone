import type { ShallowRef } from 'vue'

import type { RemoteVoiceStream, VoiceIceServer, VoiceSignal, VoiceState } from '../types'
import { screenTrackIsActive } from './voiceMedia'

const PEER_RETRY_DELAY_MS = 1_000
const MAX_PEER_RETRY_COUNT = 1

type PeerKey = `${number}:${number}`

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
  channelId: number
  userId: number
  username: string | null
  connection: RTCPeerConnection
  stream: MediaStream
  screenSender: RTCRtpSender | null
  pendingCandidates: RTCIceCandidate[]
}

interface VoicePeerRegistryOptions {
  remoteStreams: ShallowRef<RemoteVoiceStream[]>
  getActiveOptions: () => ConnectOptions | null
  getLocalStream: () => MediaStream | null
  getScreenStream: () => MediaStream | null
}

function peerKey(channelId: number, userId: number): PeerKey {
  return `${channelId}:${userId}`
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

function streamHasLiveTrack(stream: MediaStream) {
  return stream.getTracks().some((track) => track.readyState === 'live')
}

export function createVoicePeerRegistry(options: VoicePeerRegistryOptions) {
  const peers = new Map<PeerKey, PeerEntry>()
  const retryTimers = new Map<PeerKey, number>()
  const retryCounts = new Map<PeerKey, number>()

  function isActivePeer(peer: Pick<PeerEntry, 'channelId'>) {
    return options.getActiveOptions()?.channelId === peer.channelId
  }

  function replaceRemoteStream(peer: PeerEntry, patch: Partial<RemoteVoiceStream>) {
    options.remoteStreams.value = options.remoteStreams.value.map((remote) =>
      remote.channelId === peer.channelId && remote.userId === peer.userId
        ? { ...remote, ...patch }
        : remote,
    )
  }

  function removeRemoteStream(peer: Pick<PeerEntry, 'channelId' | 'userId'>) {
    options.remoteStreams.value = options.remoteStreams.value.filter(
      (remote) => remote.channelId !== peer.channelId || remote.userId !== peer.userId,
    )
  }

  function clearRetryTimer(key: PeerKey) {
    const timer = retryTimers.get(key)
    if (timer !== undefined) {
      window.clearTimeout(timer)
      retryTimers.delete(key)
    }
  }

  function closePeer(key: PeerKey) {
    const peer = peers.get(key)
    if (!peer) return
    clearRetryTimer(key)
    peer.connection.close()
    peer.stream.getTracks().forEach((track) => track.stop())
    peers.delete(key)
    removeRemoteStream(peer)
  }

  function refreshRemoteStream(peer: PeerEntry) {
    if (!streamHasLiveTrack(peer.stream)) {
      removeRemoteStream(peer)
      return
    }
    replaceRemoteStream(peer, {
      sharingScreen: screenTrackIsActive(peer.stream),
      connectionState: peer.connection.connectionState,
    })
  }

  function schedulePeerRetry(peer: PeerEntry) {
    const key = peerKey(peer.channelId, peer.userId)
    if (!isActivePeer(peer) || retryTimers.has(key)) return

    const retryCount = retryCounts.get(key) ?? 0
    if (retryCount >= MAX_PEER_RETRY_COUNT) return
    retryCounts.set(key, retryCount + 1)

    const timer = window.setTimeout(() => {
      retryTimers.delete(key)
      const currentPeer = peers.get(key)
      if (!currentPeer || !isActivePeer(currentPeer)) return
      closePeer(key)

      const activeOptions = options.getActiveOptions()
      if (!activeOptions || activeOptions.channelId !== peer.channelId) return
      if (activeOptions.currentUserId < peer.userId) {
        void createOfferFor(peer.userId, peer.username)
        return
      }
      try {
        ensurePeer(peer.userId, peer.username)
      } catch {
        // The next participant sync or voice signal will rebuild this peer.
      }
    }, PEER_RETRY_DELAY_MS)

    retryTimers.set(key, timer)
  }

  function ensurePeer(userId: number, username: string | null) {
    const activeOptions = options.getActiveOptions()
    const localStream = options.getLocalStream()
    if (!activeOptions || !localStream) {
      throw new Error('voice is not connected')
    }

    const key = peerKey(activeOptions.channelId, userId)
    const existing = peers.get(key)
    if (existing) {
      existing.username = username
      return existing
    }

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

    const peer: PeerEntry = {
      channelId: activeOptions.channelId,
      userId,
      username,
      connection,
      stream,
      screenSender,
      pendingCandidates: [],
    }
    peers.set(key, peer)

    connection.addEventListener('icecandidate', (event) => {
      const currentOptions = options.getActiveOptions()
      if (!event.candidate || !currentOptions || currentOptions.channelId !== peer.channelId) return
      currentOptions.sendSignal({
        channel_id: peer.channelId,
        target_user_id: userId,
        type: 'ice',
        candidate: event.candidate.toJSON() as Record<string, unknown>,
      })
    })
    connection.addEventListener('track', (event) => {
      if (!isActivePeer(peer)) {
        event.track.stop()
        return
      }
      if (!stream.getTracks().includes(event.track)) {
        stream.addTrack(event.track)
      }
      event.track.addEventListener('ended', () => refreshRemoteStream(peer))
      const sharingScreen = screenTrackIsActive(stream)
      const current = options.remoteStreams.value.find(
        (remote) => remote.channelId === peer.channelId && remote.userId === userId,
      )
      if (current) {
        replaceRemoteStream(peer, { stream, sharingScreen })
        return
      }
      options.remoteStreams.value = [
        ...options.remoteStreams.value,
        {
          channelId: peer.channelId,
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
      if (!isActivePeer(peer)) return
      replaceRemoteStream(peer, { connectionState: connection.connectionState })
      if (connection.connectionState === 'connected') {
        retryCounts.delete(key)
        return
      }
      if (connection.connectionState === 'failed') {
        schedulePeerRetry(peer)
        return
      }
      if (connection.connectionState === 'closed') {
        removeRemoteStream(peer)
      }
    })

    return peer
  }

  async function createOfferFor(userId: number, username: string | null) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions) return
    const peer = ensurePeer(userId, username)
    if (peer.channelId !== activeOptions.channelId || peer.connection.signalingState !== 'stable') return
    const offer = await peer.connection.createOffer()
    await peer.connection.setLocalDescription(offer)
    activeOptions.sendSignal({
      channel_id: activeOptions.channelId,
      target_user_id: userId,
      type: 'offer',
      description: { type: offer.type, sdp: offer.sdp ?? '' },
    })
  }

  async function renegotiatePeer(peer: PeerEntry) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || peer.channelId !== activeOptions.channelId) return
    if (peer.connection.signalingState !== 'stable') return
    const offer = await peer.connection.createOffer()
    await peer.connection.setLocalDescription(offer)
    activeOptions.sendSignal({
      channel_id: peer.channelId,
      target_user_id: peer.userId,
      type: 'offer',
      description: { type: offer.type, sdp: offer.sdp ?? '' },
    })
  }

  async function renegotiateAllPeers() {
    await Promise.all([...peers.values()].map((peer) => renegotiatePeer(peer)))
  }

  async function syncParticipants(participants: VoiceState[]) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || !options.getLocalStream()) return
    const activePeerIds = new Set(
      participantPeers(participants, activeOptions.currentUserId).map((participant) =>
        peerKey(activeOptions.channelId, participant.user_id),
      ),
    )
    for (const [key] of peers) {
      if (activePeerIds.has(key)) continue
      closePeer(key)
    }
    for (const participant of participantPeers(participants, activeOptions.currentUserId)) {
      if (activeOptions.currentUserId < participant.user_id) {
        await createOfferFor(participant.user_id, participant.username)
      }
    }
  }

  async function flushPendingCandidates(peer: PeerEntry) {
    if (!peer.pendingCandidates.length || !peer.connection.remoteDescription) return
    const candidates = peer.pendingCandidates.splice(0)
    for (const candidate of candidates) {
      await peer.connection.addIceCandidate(candidate)
    }
  }

  async function handleSignal(signal: VoiceSignal) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || signal.target_user_id !== activeOptions.currentUserId) return
    if (signal.channel_id !== activeOptions.channelId) return

    const peer = ensurePeer(signal.from_user_id, signal.from_username)
    if (signal.type === 'offer' && signal.description) {
      if (peer.connection.signalingState !== 'stable') {
        if (activeOptions.currentUserId < signal.from_user_id) return
        await peer.connection.setLocalDescription({ type: 'rollback' } as RTCSessionDescriptionInit)
      }
      await peer.connection.setRemoteDescription(toDescription(signal.description))
      await flushPendingCandidates(peer)
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
      if (peer.connection.signalingState === 'stable') return
      await peer.connection.setRemoteDescription(toDescription(signal.description))
      await flushPendingCandidates(peer)
      return
    }
    if (signal.type === 'ice' && signal.candidate) {
      const candidate = toIceCandidate(signal.candidate)
      if (!peer.connection.remoteDescription) {
        peer.pendingCandidates.push(candidate)
        return
      }
      await peer.connection.addIceCandidate(candidate)
    }
  }

  function closeAll() {
    retryTimers.forEach((timer) => window.clearTimeout(timer))
    retryTimers.clear()
    retryCounts.clear()
    for (const key of peers.keys()) {
      closePeer(key)
    }
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
