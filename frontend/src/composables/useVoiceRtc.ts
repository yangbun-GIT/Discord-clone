import { onBeforeUnmount, ref, shallowRef } from 'vue'

import type { RemoteVoiceStream, VoiceIceServer, VoiceSignal, VoiceState } from '../types'

type SendVoiceSignal = (payload: {
  channel_id: number
  target_user_id: number
  type: 'offer' | 'answer' | 'ice'
  description?: Record<string, unknown> | null
  candidate?: Record<string, unknown> | null
}) => void

type ConnectOptions = {
  channelId: number
  currentUserId: number
  participants: VoiceState[]
  iceServers: VoiceIceServer[]
  sendSignal: SendVoiceSignal
}

type PeerEntry = {
  connection: RTCPeerConnection
  username: string | null
  stream: MediaStream
}

const localStream = shallowRef<MediaStream | null>(null)
const remoteStreams = shallowRef<RemoteVoiceStream[]>([])
const isCapturing = ref(false)
const localSpeaking = ref(false)
const error = ref<string | null>(null)
const peers = new Map<number, PeerEntry>()
let activeOptions: ConnectOptions | null = null
let vadTimer: number | null = null
let localAnalyser: AnalyserNode | null = null
let audioContext: AudioContext | null = null

function toDescription(description: Record<string, unknown>) {
  return new RTCSessionDescription(description as unknown as RTCSessionDescriptionInit)
}

function toIceCandidate(candidate: Record<string, unknown>) {
  return new RTCIceCandidate(candidate as RTCIceCandidateInit)
}

function replaceRemoteStream(userId: number, patch: Partial<RemoteVoiceStream>) {
  remoteStreams.value = remoteStreams.value.map((remote) =>
    remote.userId === userId ? { ...remote, ...patch } : remote,
  )
}

function removeRemoteStream(userId: number) {
  remoteStreams.value = remoteStreams.value.filter((remote) => remote.userId !== userId)
}

function ensureAudioContext() {
  audioContext ??= new AudioContext()
  return audioContext
}

function attachLocalVad(stream: MediaStream) {
  const context = ensureAudioContext()
  const source = context.createMediaStreamSource(stream)
  localAnalyser = context.createAnalyser()
  localAnalyser.fftSize = 512
  source.connect(localAnalyser)
}

function startVadLoop() {
  if (vadTimer !== null || !localAnalyser) return
  const data = new Uint8Array(localAnalyser.frequencyBinCount)
  vadTimer = window.setInterval(() => {
    if (!localAnalyser) return
    localAnalyser.getByteFrequencyData(data)
    const average = data.reduce((total, value) => total + value, 0) / data.length
    localSpeaking.value = average > 18
  }, 180)
}

function stopVadLoop() {
  if (vadTimer !== null) {
    window.clearInterval(vadTimer)
    vadTimer = null
  }
  localSpeaking.value = false
  localAnalyser = null
}

function ensurePeer(userId: number, username: string | null) {
  if (!activeOptions || !localStream.value) {
    throw new Error('voice is not connected')
  }
  const existing = peers.get(userId)
  if (existing) return existing

  const stream = new MediaStream()
  const connection = new RTCPeerConnection({ iceServers: activeOptions.iceServers })
  localStream.value.getTracks().forEach((track) => {
    connection.addTrack(track, localStream.value as MediaStream)
  })

  connection.addEventListener('icecandidate', (event) => {
    if (!event.candidate || !activeOptions) return
    activeOptions.sendSignal({
      channel_id: activeOptions.channelId,
      target_user_id: userId,
      type: 'ice',
      candidate: event.candidate.toJSON() as Record<string, unknown>,
    })
  })
  connection.addEventListener('track', (event) => {
    stream.addTrack(event.track)
    const current = remoteStreams.value.find((remote) => remote.userId === userId)
    if (current) {
      replaceRemoteStream(userId, { stream })
      return
    }
    remoteStreams.value = [...remoteStreams.value, { userId, username, stream, speaking: false }]
  })
  connection.addEventListener('connectionstatechange', () => {
    if (['closed', 'disconnected', 'failed'].includes(connection.connectionState)) {
      removeRemoteStream(userId)
    }
  })

  const entry = { connection, username, stream }
  peers.set(userId, entry)
  return entry
}

async function createOfferFor(userId: number, username: string | null) {
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

function participantPeers(participants: VoiceState[], currentUserId: number) {
  return participants.filter(
    (participant) =>
      participant.channel_id !== null
      && participant.user_id !== currentUserId,
  )
}

export function useVoiceRtc() {
  async function connect(options: ConnectOptions) {
    activeOptions = options
    error.value = null
    try {
      if (!localStream.value) {
        localStream.value = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
          video: false,
        })
        attachLocalVad(localStream.value)
        startVadLoop()
      }
      isCapturing.value = true
      await syncParticipants(options.participants)
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Voice capture failed'
      disconnect()
      throw cause
    }
  }

  function disconnect() {
    peers.forEach((peer) => {
      peer.connection.close()
      peer.stream.getTracks().forEach((track) => track.stop())
    })
    peers.clear()
    localStream.value?.getTracks().forEach((track) => track.stop())
    localStream.value = null
    remoteStreams.value = []
    isCapturing.value = false
    activeOptions = null
    stopVadLoop()
  }

  async function syncParticipants(participants: VoiceState[]) {
    if (!activeOptions || !localStream.value) return
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

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    localStream,
    remoteStreams,
    isCapturing,
    localSpeaking,
    error,
    connect,
    disconnect,
    syncParticipants,
    handleSignal,
  }
}
