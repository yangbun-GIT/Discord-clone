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
import {
  P2P_VOICE_TRANSPORT_KIND,
  type VoiceTransport,
} from './voiceTransport'

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
let activeOptions: ConnectOptions | null = null
let statsTimer: number | null = null
let inputProcessor: VoiceInputProcessor | null = null
let localSpeakingReleaseTimer: number | null = null
let inputRestartTask: Promise<void> | null = null
let rtcSessionId = createRtcSessionId()

function createRtcSessionId() {
  return `rtc-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

const peerRegistry = createVoicePeerRegistry({
  remoteStreams,
  getActiveOptions: () => activeOptions,
  getLocalStream: () => localStream.value,
  getScreenStream: () => screenStream.value,
  getSessionId: () => rtcSessionId,
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

export function useVoiceRtc(): VoiceTransport {
  function handlePageHide() {
    disconnect()
  }

  window.addEventListener('pagehide', handlePageHide)

  async function connect(options: ConnectOptions) {
    if (!isCapturing.value) {
      rtcSessionId = createRtcSessionId()
    }
    activeOptions = options
    error.value = null
    errorCode.value = null
    try {
      if (!localStream.value) {
        constraintSupport.value = getSupportedVoiceConstraints()
        recordVoiceConstraintSupport(constraintSupport.value)
        const rawStream = await captureMicrophone(voiceDeviceSettings.value)
        inputProcessor = await createVoiceInputProcessor(rawStream, voiceDeviceSettings.value, {
          onInputLevel: (level) => {
            inputLevel.value = level
            updateLocalSpeakingFromInput(level)
          },
        })
        localStream.value = inputProcessor.stream
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
    if (isScreenSharing.value || screenStream.value) {
      peerRegistry.broadcastScreenState(false)
    }
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
    inputLevel.value = 0
    clearLocalSpeakingReleaseTimer()
    localSpeaking.value = false
    errorCode.value = null
    activeOptions = null
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
    const previousSettings = voiceDeviceSettings.value
    writeVoiceDeviceSettings({
      ...previousSettings,
      ...settings,
    })
    const nextSettings = readVoiceDeviceSettings()
    voiceDeviceSettings.value = nextSettings
    inputProcessor?.updateSettings(nextSettings)
    if (requiresInputProcessorRestart(previousSettings, nextSettings, settings)) {
      const restartChain = (inputRestartTask ?? Promise.resolve())
        .catch(() => undefined)
        .then(restartInputProcessor)
      const scheduledTask = restartChain.finally(() => {
        if (inputRestartTask === scheduledTask) {
          inputRestartTask = null
        }
      })
      inputRestartTask = scheduledTask
      void inputRestartTask
    }
  }

  async function restartInputProcessor() {
    if (!activeOptions || !localStream.value || !inputProcessor) return
    const previousProcessor = inputProcessor
    const previousStream = localStream.value
    const wasMuted = isMuted.value
    let nextProcessor: VoiceInputProcessor | null = null
    error.value = null
    errorCode.value = null
    try {
      constraintSupport.value = getSupportedVoiceConstraints()
      recordVoiceConstraintSupport(constraintSupport.value)
      const rawStream = await captureMicrophone(voiceDeviceSettings.value)
      nextProcessor = await createVoiceInputProcessor(rawStream, voiceDeviceSettings.value, {
        onInputLevel: (level) => {
          inputLevel.value = level
          updateLocalSpeakingFromInput(level)
        },
      })
      const [nextAudioTrack] = nextProcessor.stream.getAudioTracks()
      await peerRegistry.replaceLocalAudioTrack(nextAudioTrack ?? null)
      inputProcessor = nextProcessor
      localStream.value = nextProcessor.stream
      setAudioTracksMuted(localStream.value, wasMuted)
      previousProcessor.close()
      stopMediaStream(previousStream)
      void refreshVoiceDevices()
    } catch (cause) {
      nextProcessor?.close()
      const mediaError = cause instanceof VoiceMediaError ? normalizeMediaError(cause, 'microphone') : null
      errorCode.value = mediaError?.code ?? null
      error.value = mediaError?.message ?? (cause instanceof Error ? cause.message : 'Microphone settings reload failed')
    }
  }

  function setMuted(muted: boolean) {
    isMuted.value = muted
    setAudioTracksMuted(localStream.value, muted)
    if (muted) {
      clearLocalSpeakingReleaseTimer()
      localSpeaking.value = false
    }
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

  function clearError() {
    error.value = null
    errorCode.value = null
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

  function clearLocalSpeakingReleaseTimer() {
    if (localSpeakingReleaseTimer === null) return
    window.clearTimeout(localSpeakingReleaseTimer)
    localSpeakingReleaseTimer = null
  }

  function updateLocalSpeakingFromInput(level: number) {
    if (isMuted.value || !isCapturing.value) {
      clearLocalSpeakingReleaseTimer()
      localSpeaking.value = false
      return
    }
    const threshold = Math.max(8, voiceDeviceSettings.value.inputSensitivity - 12)
    if (level >= threshold) {
      clearLocalSpeakingReleaseTimer()
      localSpeaking.value = true
      return
    }
    if (!localSpeaking.value || localSpeakingReleaseTimer !== null) return
    localSpeakingReleaseTimer = window.setTimeout(() => {
      localSpeakingReleaseTimer = null
      localSpeaking.value = false
    }, 850)
  }

  function requiresInputProcessorRestart(
    previousSettings: VoiceDeviceSettings,
    nextSettings: VoiceDeviceSettings,
    patch: Partial<VoiceDeviceSettings>,
  ) {
    if (!activeOptions || !localStream.value) return false
    return (
      ('inputDeviceId' in patch && previousSettings.inputDeviceId !== nextSettings.inputDeviceId)
      || ('noiseSuppressionMode' in patch && previousSettings.noiseSuppressionMode !== nextSettings.noiseSuppressionMode)
      || ('rnnoiseSuppression' in patch && previousSettings.rnnoiseSuppression !== nextSettings.rnnoiseSuppression)
    )
  }

  return {
    kind: P2P_VOICE_TRANSPORT_KIND,
    getSessionId: () => rtcSessionId,
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
    clearError,
    syncParticipants,
    handleSignal,
    refreshVoiceDevices,
    updateVoiceDeviceSettings,
  }
}
