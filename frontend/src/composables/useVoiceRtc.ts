import { onBeforeUnmount, ref, shallowRef } from 'vue'

import type {
  RemoteVoiceStream,
  VoiceIceServer,
  VoiceQualityStats,
  VoiceSignal,
  VoiceState,
} from '../types'

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
  screenSender: RTCRtpSender | null
}

const localStream = shallowRef<MediaStream | null>(null)
const screenStream = shallowRef<MediaStream | null>(null)
const remoteStreams = shallowRef<RemoteVoiceStream[]>([])
const isCapturing = ref(false)
const isMuted = ref(false)
const isScreenSharing = ref(false)
const localSpeaking = ref(false)
const inputLevel = ref(0)
const error = ref<string | null>(null)
const qualityStats = ref<VoiceQualityStats>(createEmptyQualityStats())
const peers = new Map<number, PeerEntry>()
let activeOptions: ConnectOptions | null = null
let vadTimer: number | null = null
let statsTimer: number | null = null
let localAnalyser: AnalyserNode | null = null
let audioContext: AudioContext | null = null
const previousOutboundBytes = new Map<string, { bytes: number; timestamp: number }>()

function createEmptyQualityStats(): VoiceQualityStats {
  return {
    peerCount: 0,
    connectedPeerCount: 0,
    averageRoundTripTimeMs: null,
    inboundAudioPacketsLost: 0,
    inboundAudioJitterMs: null,
    outboundAudioBitrateKbps: null,
    outboundScreenBitrateKbps: null,
  }
}

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

function screenTrackIsActive(stream: MediaStream) {
  return stream.getVideoTracks().some((track) => track.readyState === 'live')
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
    inputLevel.value = Math.round(Math.min(100, (average / 90) * 100))
    localSpeaking.value = average > 18
  }, 180)
}

function stopVadLoop() {
  if (vadTimer !== null) {
    window.clearInterval(vadTimer)
    vadTimer = null
  }
  localSpeaking.value = false
  inputLevel.value = 0
  localAnalyser = null
}

function numericStat(report: RTCStats, key: string) {
  const value = (report as unknown as Record<string, unknown>)[key]
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function stringStat(report: RTCStats, key: string) {
  const value = (report as unknown as Record<string, unknown>)[key]
  return typeof value === 'string' ? value : null
}

function mediaKind(report: RTCStats) {
  return stringStat(report, 'kind') ?? stringStat(report, 'mediaType')
}

function updateBitrateSamples(
  userId: number,
  report: RTCStats,
  audioBitrates: number[],
  screenBitrates: number[],
) {
  const bytesSent = numericStat(report, 'bytesSent')
  const kind = mediaKind(report)
  if (bytesSent === null || !kind) return

  const key = `${userId}:${report.id}`
  const previous = previousOutboundBytes.get(key)
  previousOutboundBytes.set(key, { bytes: bytesSent, timestamp: report.timestamp })
  if (!previous || report.timestamp <= previous.timestamp) return

  const bitrateKbps = ((bytesSent - previous.bytes) * 8) / (report.timestamp - previous.timestamp)
  if (!Number.isFinite(bitrateKbps) || bitrateKbps < 0) return
  if (kind === 'audio') {
    audioBitrates.push(bitrateKbps)
    return
  }
  if (kind === 'video') {
    screenBitrates.push(bitrateKbps)
  }
}

function average(values: number[]) {
  if (!values.length) return null
  return values.reduce((total, value) => total + value, 0) / values.length
}

async function collectQualityStats() {
  const nextStats = createEmptyQualityStats()
  nextStats.peerCount = peers.size
  nextStats.connectedPeerCount = [...peers.values()].filter(
    (peer) => peer.connection.connectionState === 'connected',
  ).length

  const roundTripSamples: number[] = []
  const jitterSamples: number[] = []
  const audioBitrates: number[] = []
  const screenBitrates: number[] = []

  for (const [userId, peer] of peers) {
    const report = await peer.connection.getStats()
    report.forEach((entry) => {
      if (entry.type === 'candidate-pair' && numericStat(entry, 'currentRoundTripTime') !== null) {
        roundTripSamples.push((numericStat(entry, 'currentRoundTripTime') as number) * 1000)
      }
      if (entry.type === 'remote-inbound-rtp' && numericStat(entry, 'roundTripTime') !== null) {
        roundTripSamples.push((numericStat(entry, 'roundTripTime') as number) * 1000)
      }
      if (entry.type === 'inbound-rtp' && mediaKind(entry) === 'audio') {
        nextStats.inboundAudioPacketsLost += numericStat(entry, 'packetsLost') ?? 0
        const jitter = numericStat(entry, 'jitter')
        if (jitter !== null) {
          jitterSamples.push(jitter * 1000)
        }
      }
      if (entry.type === 'outbound-rtp') {
        updateBitrateSamples(userId, entry, audioBitrates, screenBitrates)
      }
    })
  }

  nextStats.averageRoundTripTimeMs = average(roundTripSamples)
  nextStats.inboundAudioJitterMs = average(jitterSamples)
  nextStats.outboundAudioBitrateKbps = average(audioBitrates)
  nextStats.outboundScreenBitrateKbps = average(screenBitrates)
  qualityStats.value = nextStats
}

function startStatsLoop() {
  if (statsTimer !== null) return
  statsTimer = window.setInterval(() => {
    void collectQualityStats().catch(() => {
      qualityStats.value = createEmptyQualityStats()
    })
  }, 2000)
  void collectQualityStats()
}

function stopStatsLoop() {
  if (statsTimer !== null) {
    window.clearInterval(statsTimer)
    statsTimer = null
  }
  previousOutboundBytes.clear()
  qualityStats.value = createEmptyQualityStats()
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
  const screenTrack = screenStream.value?.getVideoTracks()[0]
  let screenSender: RTCRtpSender | null = null
  if (screenTrack && screenTrack.readyState === 'live') {
    screenSender = connection.addTrack(screenTrack, screenStream.value as MediaStream)
  }

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
    const sharingScreen = screenTrackIsActive(stream)
    if (current) {
      replaceRemoteStream(userId, { stream, sharingScreen })
      return
    }
    remoteStreams.value = [
      ...remoteStreams.value,
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
      setMuted(isMuted.value)
      startStatsLoop()
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
    screenStream.value?.getTracks().forEach((track) => track.stop())
    localStream.value = null
    screenStream.value = null
    remoteStreams.value = []
    isCapturing.value = false
    isMuted.value = false
    isScreenSharing.value = false
    activeOptions = null
    stopVadLoop()
    stopStatsLoop()
    void audioContext?.close()
    audioContext = null
  }

  function setMuted(muted: boolean) {
    isMuted.value = muted
    localStream.value?.getAudioTracks().forEach((track) => {
      track.enabled = !muted
    })
  }

  function toggleMute() {
    setMuted(!isMuted.value)
  }

  async function startScreenShare() {
    if (!activeOptions || !localStream.value) {
      throw new Error('voice is not connected')
    }
    error.value = null
    try {
      const displayStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          frameRate: { ideal: 15, max: 30 },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      })
      screenStream.value = displayStream
      isScreenSharing.value = true
      const [track] = displayStream.getVideoTracks()
      track.addEventListener('ended', () => {
        void stopScreenShare()
      })
      for (const peer of peers.values()) {
        if (peer.screenSender) {
          await peer.screenSender.replaceTrack(track)
        } else {
          peer.screenSender = peer.connection.addTrack(track, displayStream)
        }
      }
      await renegotiateAllPeers()
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Screen sharing failed'
      throw cause
    }
  }

  async function stopScreenShare() {
    const previousStream = screenStream.value
    screenStream.value = null
    isScreenSharing.value = false
    previousStream?.getTracks().forEach((track) => track.stop())
    for (const peer of peers.values()) {
      if (!peer.screenSender) continue
      peer.connection.removeTrack(peer.screenSender)
      peer.screenSender = null
    }
    await renegotiateAllPeers()
  }

  async function toggleScreenShare() {
    if (isScreenSharing.value) {
      await stopScreenShare()
      return
    }
    await startScreenShare()
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
    screenStream,
    remoteStreams,
    isCapturing,
    isMuted,
    isScreenSharing,
    localSpeaking,
    inputLevel,
    error,
    qualityStats,
    connect,
    disconnect,
    toggleMute,
    toggleScreenShare,
    syncParticipants,
    handleSignal,
  }
}
