import type { ShallowRef } from 'vue'

import type { RemoteVoiceStream, VoiceSignal, VoiceState } from '../types'
import { calculateRms, rmsToInputLevelPercent, screenTrackIsActive } from './voiceMedia'
import type {
  SendVoiceTransportSignal,
  VoiceTransportConnectOptions,
} from './voiceTransport'

const PEER_RETRY_DELAY_MS = 1_000
const MAX_PEER_RETRY_COUNT = 1
const SIGNALING_STABLE_WAIT_MS = 2_000
const REMOTE_SPEAKING_THRESHOLD = 12
const REMOTE_SPEAKING_RELEASE_MS = 900

type PeerKey = `${number}:${number}`

export type SendVoiceSignal = SendVoiceTransportSignal

export type ConnectOptions = VoiceTransportConnectOptions

export type PeerEntry = {
  channelId: number
  userId: number
  username: string | null
  connection: RTCPeerConnection
  stream: MediaStream
  screenSender: RTCRtpSender | null
  screenTransceiver: RTCRtpTransceiver | null
  pendingCandidates: RTCIceCandidate[]
}

type RemoteSpeakingMonitor = {
  context: AudioContext
  intervalId: number
  releaseTimer: number | null
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

function waitForStableSignaling(connection: RTCPeerConnection) {
  if (connection.signalingState === 'stable') return Promise.resolve(true)
  return new Promise<boolean>((resolve) => {
    const timer = window.setTimeout(() => {
      connection.removeEventListener('signalingstatechange', handleChange)
      resolve(false)
    }, SIGNALING_STABLE_WAIT_MS)
    function handleChange() {
      if (connection.signalingState !== 'stable') return
      window.clearTimeout(timer)
      connection.removeEventListener('signalingstatechange', handleChange)
      resolve(true)
    }
    connection.addEventListener('signalingstatechange', handleChange)
  })
}

function canCreateAnswer(connection: RTCPeerConnection) {
  return (
    connection.signalingState === 'have-remote-offer'
    || connection.signalingState === 'have-local-pranswer'
  )
}

function canApplyAnswer(connection: RTCPeerConnection) {
  return (
    connection.signalingState === 'have-local-offer'
    || connection.signalingState === 'have-remote-pranswer'
  )
}

function isMLineOrderError(error: unknown) {
  return error instanceof Error && error.message.includes('m-lines')
}

async function rollbackLocalDescription(connection: RTCPeerConnection) {
  try {
    await connection.setLocalDescription({ type: 'rollback' } as RTCSessionDescriptionInit)
    return true
  } catch {
    return false
  }
}

async function setRemoteDescriptionIfValid(
  connection: RTCPeerConnection,
  description: Record<string, unknown>,
) {
  try {
    await connection.setRemoteDescription(toDescription(description))
    return true
  } catch {
    return false
  }
}

export function createVoicePeerRegistry(options: VoicePeerRegistryOptions) {
  const peers = new Map<PeerKey, PeerEntry>()
  const retryTimers = new Map<PeerKey, number>()
  const retryCounts = new Map<PeerKey, number>()
  const signalQueues = new Map<PeerKey, Promise<void>>()
  const remoteSpeakingMonitors = new Map<PeerKey, RemoteSpeakingMonitor>()
  const remoteScreenStates = new Map<PeerKey, boolean>()

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
    stopRemoteSpeakingMonitor(key)
    remoteScreenStates.delete(key)
    peer.connection.close()
    peer.stream.getTracks().forEach((track) => track.stop())
    peers.delete(key)
    signalQueues.delete(key)
    removeRemoteStream(peer)
  }

  function localScreenShareIsActive() {
    const screenStream = options.getScreenStream()
    const screenTrack = screenStream?.getVideoTracks()[0]
    return Boolean(screenTrack && screenTrack.readyState === 'live')
  }

  function sendScreenStateToPeer(peer: PeerEntry, sharingScreen: boolean) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || peer.channelId !== activeOptions.channelId) return
    activeOptions.sendSignal({
      channel_id: peer.channelId,
      target_user_id: peer.userId,
      type: 'screen',
      screen_sharing: sharingScreen,
    })
  }

  function peerIsSharingScreen(peer: PeerEntry) {
    const explicitState = remoteScreenStates.get(peerKey(peer.channelId, peer.userId))
    if (explicitState !== undefined) return explicitState
    return screenTrackIsActive(peer.stream)
  }

  function refreshRemoteStream(peer: PeerEntry) {
    if (!streamHasLiveTrack(peer.stream)) {
      removeRemoteStream(peer)
      return
    }
    replaceRemoteStream(peer, {
      sharingScreen: peerIsSharingScreen(peer),
      connectionState: peer.connection.connectionState,
    })
  }

  function setRemoteSpeaking(peer: PeerEntry, speaking: boolean) {
    replaceRemoteStream(peer, { speaking })
  }

  function stopRemoteSpeakingMonitor(key: PeerKey) {
    const monitor = remoteSpeakingMonitors.get(key)
    if (!monitor) return
    window.clearInterval(monitor.intervalId)
    if (monitor.releaseTimer !== null) window.clearTimeout(monitor.releaseTimer)
    void monitor.context.close().catch(() => {})
    remoteSpeakingMonitors.delete(key)
  }

  function startRemoteSpeakingMonitor(peer: PeerEntry) {
    const key = peerKey(peer.channelId, peer.userId)
    if (remoteSpeakingMonitors.has(key) || !peer.stream.getAudioTracks().length) return
    const AudioContextConstructor = window.AudioContext
    if (!AudioContextConstructor) return

    const context = new AudioContextConstructor()
    const source = context.createMediaStreamSource(peer.stream)
    const analyser = context.createAnalyser()
    const samples = new Float32Array(512)
    analyser.fftSize = 512
    analyser.smoothingTimeConstant = 0
    source.connect(analyser)

    const monitor: RemoteSpeakingMonitor = {
      context,
      intervalId: 0,
      releaseTimer: null,
    }
    monitor.intervalId = window.setInterval(() => {
      if (!peers.has(key) || !isActivePeer(peer)) return
      analyser.getFloatTimeDomainData(samples)
      const level = rmsToInputLevelPercent(calculateRms(samples))
      if (level >= REMOTE_SPEAKING_THRESHOLD) {
        if (monitor.releaseTimer !== null) {
          window.clearTimeout(monitor.releaseTimer)
          monitor.releaseTimer = null
        }
        setRemoteSpeaking(peer, true)
        return
      }
      if (monitor.releaseTimer !== null) return
      monitor.releaseTimer = window.setTimeout(() => {
        monitor.releaseTimer = null
        setRemoteSpeaking(peer, false)
      }, REMOTE_SPEAKING_RELEASE_MS)
    }, 120)
    remoteSpeakingMonitors.set(key, monitor)
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
    let screenTransceiver: RTCRtpTransceiver | null = null
    let screenSender: RTCRtpSender | null = null
    if (screenTrack && screenTrack.readyState === 'live' && screenStream) {
      screenTransceiver = connection.addTransceiver(screenTrack, {
        direction: 'sendrecv',
        streams: [screenStream],
      })
      screenSender = screenTransceiver.sender
    } else {
      screenTransceiver = connection.addTransceiver('video', { direction: 'sendrecv' })
      screenSender = screenTransceiver.sender
    }

    const peer: PeerEntry = {
      channelId: activeOptions.channelId,
      userId,
      username,
      connection,
      stream,
      screenSender,
      screenTransceiver,
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
      if (event.track.kind === 'audio') startRemoteSpeakingMonitor(peer)
      event.track.addEventListener('ended', () => refreshRemoteStream(peer))
      event.track.addEventListener('mute', () => refreshRemoteStream(peer))
      event.track.addEventListener('unmute', () => refreshRemoteStream(peer))
      window.setTimeout(() => refreshRemoteStream(peer), 0)
      window.setTimeout(() => refreshRemoteStream(peer), 250)
      const sharingScreen = peerIsSharingScreen(peer)
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
    await runQueuedSignal(peer, async () => {
      const currentOptions = options.getActiveOptions()
      if (!currentOptions || peer.channelId !== currentOptions.channelId) return
      if (!(await waitForStableSignaling(peer.connection))) return
      const offer = await peer.connection.createOffer()
      try {
        await peer.connection.setLocalDescription(offer)
      } catch (error) {
        handleLocalOfferFailure(peer, error)
        return
      }
      currentOptions.sendSignal({
        channel_id: currentOptions.channelId,
        target_user_id: userId,
        type: 'offer',
        description: { type: offer.type, sdp: offer.sdp ?? '' },
      })
      if (localScreenShareIsActive()) {
        sendScreenStateToPeer(peer, true)
      }
    })
  }

  async function renegotiatePeer(peer: PeerEntry) {
    await runQueuedSignal(peer, async () => {
      const activeOptions = options.getActiveOptions()
      if (!activeOptions || peer.channelId !== activeOptions.channelId) return
      if (!(await waitForStableSignaling(peer.connection))) return
      const offer = await peer.connection.createOffer()
      try {
        await peer.connection.setLocalDescription(offer)
      } catch (error) {
        handleLocalOfferFailure(peer, error)
        return
      }
      activeOptions.sendSignal({
        channel_id: peer.channelId,
        target_user_id: peer.userId,
        type: 'offer',
        description: { type: offer.type, sdp: offer.sdp ?? '' },
      })
      if (localScreenShareIsActive()) {
        sendScreenStateToPeer(peer, true)
      }
    })
  }

  async function renegotiateAllPeers() {
    await Promise.all([...peers.values()].map((peer) => renegotiatePeer(peer)))
  }

  async function replaceLocalAudioTrack(track: MediaStreamTrack | null) {
    await Promise.all([...peers.values()].map(async (peer) => {
      const sender = peer.connection.getSenders().find((candidate) => candidate.track?.kind === 'audio')
      if (!sender) return
      await sender.replaceTrack(track)
    }))
  }

  function broadcastScreenState(sharingScreen: boolean) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions) return
    for (const peer of peers.values()) {
      if (peer.channelId !== activeOptions.channelId) continue
      activeOptions.sendSignal({
        channel_id: peer.channelId,
        target_user_id: peer.userId,
        type: 'screen',
        screen_sharing: sharingScreen,
      })
    }
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

  async function runQueuedSignal(peer: PeerEntry, task: () => Promise<void>) {
    const key = peerKey(peer.channelId, peer.userId)
    const previous = signalQueues.get(key) ?? Promise.resolve()
    const current = previous.catch(() => undefined).then(async () => {
      if (peers.get(key) !== peer || peer.connection.connectionState === 'closed') return
      await task()
    })
    signalQueues.set(key, current.catch(() => undefined))
    await current
  }

  function handleLocalOfferFailure(peer: PeerEntry, error: unknown) {
    if (!isMLineOrderError(error)) throw error
    closePeer(peerKey(peer.channelId, peer.userId))
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || activeOptions.channelId !== peer.channelId) return
    if (activeOptions.currentUserId >= peer.userId) return
    window.setTimeout(() => {
      const currentOptions = options.getActiveOptions()
      if (!currentOptions || currentOptions.channelId !== peer.channelId) return
      void createOfferFor(peer.userId, peer.username)
    }, 0)
  }

  async function handleSignal(signal: VoiceSignal) {
    const activeOptions = options.getActiveOptions()
    if (!activeOptions || signal.target_user_id !== activeOptions.currentUserId) return
    if (signal.channel_id !== activeOptions.channelId) return

    const peer = ensurePeer(signal.from_user_id, signal.from_username)
    await runQueuedSignal(peer, async () => {
      const currentOptions = options.getActiveOptions()
      if (!currentOptions || signal.target_user_id !== currentOptions.currentUserId) return
      if (signal.channel_id !== currentOptions.channelId || peer.channelId !== currentOptions.channelId) return

      if (signal.type === 'screen') {
        remoteScreenStates.set(peerKey(peer.channelId, peer.userId), Boolean(signal.screen_sharing))
        replaceRemoteStream(peer, { sharingScreen: Boolean(signal.screen_sharing) })
        return
      }
      if (signal.type === 'offer' && signal.description) {
        if (peer.connection.signalingState !== 'stable') {
          if (currentOptions.currentUserId < signal.from_user_id) return
          if (!(await rollbackLocalDescription(peer.connection))) return
        }
        if (!(await setRemoteDescriptionIfValid(peer.connection, signal.description))) return
        if (!canCreateAnswer(peer.connection)) return
        await flushPendingCandidates(peer)
        const answer = await peer.connection.createAnswer()
        await peer.connection.setLocalDescription(answer)
        currentOptions.sendSignal({
          channel_id: currentOptions.channelId,
          target_user_id: signal.from_user_id,
          type: 'answer',
          description: { type: answer.type, sdp: answer.sdp ?? '' },
        })
        if (localScreenShareIsActive()) {
          sendScreenStateToPeer(peer, true)
        }
        return
      }
      if (signal.type === 'answer' && signal.description) {
        if (!canApplyAnswer(peer.connection)) return
        if (!(await setRemoteDescriptionIfValid(peer.connection, signal.description))) return
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
    })
  }

  function closeAll() {
    retryTimers.forEach((timer) => window.clearTimeout(timer))
    retryTimers.clear()
    retryCounts.clear()
    remoteScreenStates.clear()
    for (const key of remoteSpeakingMonitors.keys()) {
      stopRemoteSpeakingMonitor(key)
    }
    for (const key of peers.keys()) {
      closePeer(key)
    }
    options.remoteStreams.value = []
  }

  return {
    peers,
    closeAll,
    broadcastScreenState,
    renegotiateAllPeers,
    replaceLocalAudioTrack,
    syncParticipants,
    handleSignal,
  }
}
