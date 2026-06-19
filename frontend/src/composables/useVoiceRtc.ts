import { onBeforeUnmount, ref, shallowRef } from 'vue'

import type {
  RemoteVoiceStream,
  VoiceQualityStats,
  VoiceSignal,
  VoiceState,
} from '../types'
import {
  captureDisplay,
  captureMicrophone,
  createVoiceInputProcessor,
  getSupportedVoiceConstraints,
  listVoiceDevices,
  normalizeMediaError,
  readVoiceDeviceSettings,
  recordVoiceConstraintSupport,
  VoiceMediaError,
  writeVoiceDeviceSettings,
  type VoiceDeviceList,
  type VoiceDeviceSettings,
  type VoiceInputProcessor,
  type VoiceConstraintSupport,
  type VoiceMediaErrorCode,
  setAudioTracksMuted,
  stopMediaStream,
} from './voiceMedia'
import {
  createVoicePeerRegistry,
  type ConnectOptions,
} from './voicePeerConnections'
import { createEmptyQualityStats, createVoiceStatsCollector } from './voiceStats'
import { createVoiceVad } from './voiceVad'

const localStream = shallowRef<MediaStream | null>(null)
const screenStream = shallowRef<MediaStream | null>(null)
const remoteStreams = shallowRef<RemoteVoiceStream[]>([])
const isCapturing = ref(false)
const isMuted = ref(false)
const isScreenSharing = ref(false)
const localSpeaking = ref(false)
const inputLevel = ref(0)
const error = ref<string | null>(null)
const errorCode = ref<VoiceMediaErrorCode | null>(null)
const constraintSupport = ref<VoiceConstraintSupport>(getSupportedVoiceConstraints())
const voiceDeviceSettings = ref<VoiceDeviceSettings>(readVoiceDeviceSettings())
const voiceDevices = ref<VoiceDeviceList>({ inputs: [], outputs: [] })
const qualityStats = ref<VoiceQualityStats>(createEmptyQualityStats())
const voiceStatsCollector = createVoiceStatsCollector()
const voiceVad = createVoiceVad({ inputLevel, localSpeaking })
let activeOptions: ConnectOptions | null = null
let statsTimer: number | null = null
let inputProcessor: VoiceInputProcessor | null = null

const peerRegistry = createVoicePeerRegistry({
  remoteStreams,
  getActiveOptions: () => activeOptions,
  getLocalStream: () => localStream.value,
  getScreenStream: () => screenStream.value,
})

async function collectQualityStats() {
  qualityStats.value = await voiceStatsCollector.collect(peerRegistry.peers)
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
  voiceStatsCollector.reset()
  qualityStats.value = createEmptyQualityStats()
}

export function useVoiceRtc() {
  function handlePageHide() {
    disconnect()
  }

  window.addEventListener('pagehide', handlePageHide)

  async function connect(options: ConnectOptions) {
    activeOptions = options
    error.value = null
    errorCode.value = null
    try {
      if (!localStream.value) {
        constraintSupport.value = getSupportedVoiceConstraints()
        recordVoiceConstraintSupport(constraintSupport.value)
        const rawStream = await captureMicrophone(voiceDeviceSettings.value)
        inputProcessor = createVoiceInputProcessor(rawStream, voiceDeviceSettings.value)
        localStream.value = inputProcessor.stream
        voiceVad.attach(localStream.value)
        voiceVad.start()
        void refreshVoiceDevices()
      }
      isCapturing.value = true
      setMuted(isMuted.value)
      startStatsLoop()
      await syncParticipants(options.participants)
    } catch (cause) {
      const mediaError = cause instanceof VoiceMediaError ? normalizeMediaError(cause, 'microphone') : null
      disconnect()
      errorCode.value = mediaError?.code ?? null
      error.value = mediaError?.message ?? (cause instanceof Error ? cause.message : 'Voice connection failed')
      throw mediaError ?? cause
    }
  }

  function disconnect() {
    peerRegistry.closeAll()
    if (inputProcessor) {
      inputProcessor.close()
      inputProcessor = null
    } else {
      stopMediaStream(localStream.value)
    }
    stopMediaStream(screenStream.value)
    localStream.value = null
    screenStream.value = null
    isCapturing.value = false
    isMuted.value = false
    isScreenSharing.value = false
    errorCode.value = null
    activeOptions = null
    voiceVad.close()
    stopStatsLoop()
  }

  async function refreshVoiceDevices() {
    try {
      voiceDevices.value = await listVoiceDevices()
    } catch {
      voiceDevices.value = { inputs: [], outputs: [] }
    }
  }

  function updateVoiceDeviceSettings(settings: Partial<VoiceDeviceSettings>) {
    writeVoiceDeviceSettings({
      ...voiceDeviceSettings.value,
      ...settings,
    })
    voiceDeviceSettings.value = readVoiceDeviceSettings()
    inputProcessor?.updateSettings(voiceDeviceSettings.value)
  }

  function setMuted(muted: boolean) {
    isMuted.value = muted
    setAudioTracksMuted(localStream.value, muted)
  }

  function toggleMute() {
    setMuted(!isMuted.value)
  }

  async function startScreenShare() {
    if (!activeOptions || !localStream.value) {
      throw new Error('voice is not connected')
    }
    error.value = null
    errorCode.value = null
    try {
      const displayStream = await captureDisplay()
      screenStream.value = displayStream
      isScreenSharing.value = true
      const [track] = displayStream.getVideoTracks()
      track.addEventListener('ended', () => {
        void stopScreenShare()
      })
      for (const peer of peerRegistry.peers.values()) {
        if (peer.screenTransceiver) {
          await peer.screenTransceiver.sender.replaceTrack(track)
          peer.screenTransceiver.direction = 'sendrecv'
          peer.screenSender = peer.screenTransceiver.sender
        } else if (peer.screenSender) {
          await peer.screenSender.replaceTrack(track)
        } else {
          peer.screenSender = peer.connection.addTrack(track, displayStream)
        }
      }
      await peerRegistry.renegotiateAllPeers()
      peerRegistry.broadcastScreenState(true)
    } catch (cause) {
      const mediaError = cause instanceof VoiceMediaError ? normalizeMediaError(cause, 'screen') : null
      errorCode.value = mediaError?.code ?? null
      error.value = mediaError?.message ?? (cause instanceof Error ? cause.message : 'Screen sharing failed')
      throw mediaError ?? cause
    }
  }

  async function stopScreenShare() {
    const previousStream = screenStream.value
    screenStream.value = null
    isScreenSharing.value = false
    stopMediaStream(previousStream)
    for (const peer of peerRegistry.peers.values()) {
      if (!peer.screenSender) continue
      await peer.screenSender.replaceTrack(null)
      if (peer.screenTransceiver) {
        peer.screenTransceiver.direction = 'sendrecv'
        peer.screenSender = peer.screenTransceiver.sender
      } else {
        peer.connection.removeTrack(peer.screenSender)
        peer.screenSender = null
      }
    }
    peerRegistry.broadcastScreenState(false)
    await peerRegistry.renegotiateAllPeers()
  }

  async function toggleScreenShare() {
    if (isScreenSharing.value) {
      await stopScreenShare()
      return
    }
    await startScreenShare()
  }

  async function syncParticipants(participants: VoiceState[]) {
    await peerRegistry.syncParticipants(participants)
  }

  async function handleSignal(signal: VoiceSignal) {
    await peerRegistry.handleSignal(signal)
  }

  onBeforeUnmount(() => {
    window.removeEventListener('pagehide', handlePageHide)
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
    errorCode,
    constraintSupport,
    voiceDeviceSettings,
    voiceDevices,
    qualityStats,
    connect,
    disconnect,
    setMuted,
    toggleMute,
    toggleScreenShare,
    syncParticipants,
    handleSignal,
    refreshVoiceDevices,
    updateVoiceDeviceSettings,
  }
}
