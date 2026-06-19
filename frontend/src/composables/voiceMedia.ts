import rnnoiseWasmPath from '@sapphi-red/web-noise-suppressor/rnnoise.wasm?url'
import rnnoiseSimdWasmPath from '@sapphi-red/web-noise-suppressor/rnnoise_simd.wasm?url'
import rnnoiseWorkletPath from '@sapphi-red/web-noise-suppressor/rnnoiseWorklet.js?url'

const MEDIA_PERMISSION_TIMEOUT_MS = 30_000
const VOICE_CONSTRAINT_SUPPORT_KEY = 'discord_clone_voice_constraint_support'
const VOICE_PROCESSING_SETTINGS_KEY = 'discord_clone_voice_processing_settings'
const VOICE_DEVICE_SETTINGS_KEY = 'discord_clone_voice_device_settings'
const SILENCE_DB = -64
const SPEECH_REFERENCE_DB = -18
const GATE_HOLD_MS = 4_800
const GATE_ATTENUATED_GAIN = 0.38

type RnnoiseNode = AudioNode & { destroy: () => void }

type ExtendedMediaTrackSupportedConstraints = MediaTrackSupportedConstraints & {
  latency?: boolean
}

type ExtendedMediaTrackConstraints = MediaTrackConstraints & {
  latency?: ConstrainDouble
}

export type VoiceMediaErrorCode =
  | 'media-unsupported'
  | 'insecure-context'
  | 'permission-denied'
  | 'no-device'
  | 'device-busy'
  | 'constraints-unsatisfied'
  | 'permission-timeout'
  | 'screen-permission-denied'
  | 'screen-unavailable'
  | 'screen-timeout'
  | 'unknown'

export interface VoiceConstraintSupport {
  echoCancellation: boolean
  noiseSuppression: boolean
  autoGainControl: boolean
  channelCount: boolean
  sampleRate: boolean
  sampleSize: boolean
  latency: boolean
}

export interface VoiceProcessingSettings {
  mode: VoiceProcessingMode
  echoCancellation: boolean
  noiseSuppression: boolean
  autoGainControl: boolean
}

export type VoiceProcessingMode = 'balanced' | 'speech-stability' | 'raw' | 'custom'

export interface VoiceDeviceSettings {
  inputDeviceId: string | null
  outputDeviceId: string | null
  inputVolume: number
  outputVolume: number
  inputSensitivity: number
  noiseGate: boolean
  rnnoiseSuppression: boolean
}

export interface VoiceDeviceOption {
  id: string
  label: string
  kind: 'audioinput' | 'audiooutput'
  isDefault: boolean
}

export interface VoiceDeviceList {
  inputs: VoiceDeviceOption[]
  outputs: VoiceDeviceOption[]
}

export interface VoiceInputProcessor {
  stream: MediaStream
  updateSettings: (settings: VoiceDeviceSettings) => void
  close: () => void
}

export interface VoiceInputProcessorOptions {
  onInputLevel?: (level: number) => void
}

export class VoiceMediaError extends Error {
  constructor(
    public readonly code: VoiceMediaErrorCode,
    message: string,
    public readonly cause?: unknown,
  ) {
    super(message)
    this.name = 'VoiceMediaError'
  }
}

export async function captureMicrophone(settings: VoiceDeviceSettings = readVoiceDeviceSettings()) {
  assertMicrophoneCaptureAvailable()
  return requestStreamWithTimeout(
    navigator.mediaDevices.getUserMedia({
      audio: buildAudioConstraints(
        getSupportedVoiceConstraints(),
        readVoiceProcessingSettings(),
        settings,
      ),
      video: false,
    }),
    'permission-timeout',
  ).catch((error: unknown) => {
    throw normalizeMediaError(error, 'microphone')
  })
}

export function defaultVoiceDeviceSettings(): VoiceDeviceSettings {
  return {
    inputDeviceId: null,
    outputDeviceId: null,
    inputVolume: 82,
    outputVolume: 100,
    inputSensitivity: 38,
    noiseGate: true,
    rnnoiseSuppression: true,
  }
}

export function readVoiceDeviceSettings(): VoiceDeviceSettings {
  try {
    const value = getLocalStorage()?.getItem(VOICE_DEVICE_SETTINGS_KEY)
    if (!value) return defaultVoiceDeviceSettings()
    const parsed = JSON.parse(value) as Partial<VoiceDeviceSettings>
    return normalizeVoiceDeviceSettings(parsed)
  } catch {
    return defaultVoiceDeviceSettings()
  }
}

export function writeVoiceDeviceSettings(settings: VoiceDeviceSettings) {
  try {
    getLocalStorage()?.setItem(
      VOICE_DEVICE_SETTINGS_KEY,
      JSON.stringify(normalizeVoiceDeviceSettings(settings)),
    )
  } catch {
    // Voice device preferences are best-effort and should not block voice controls.
  }
}

export async function listVoiceDevices(): Promise<VoiceDeviceList> {
  if (!navigator.mediaDevices?.enumerateDevices) return { inputs: [], outputs: [] }
  const devices = await navigator.mediaDevices.enumerateDevices()
  const inputs = devices
    .filter((device) => device.kind === 'audioinput')
    .map((device, index) => voiceDeviceOption(device, index, 'audioinput'))
  const outputs = devices
    .filter((device) => device.kind === 'audiooutput')
    .map((device, index) => voiceDeviceOption(device, index, 'audiooutput'))
  return { inputs, outputs }
}

export function defaultVoiceProcessingSettings(): VoiceProcessingSettings {
  return voiceProcessingPreset('speech-stability')
}

export function voiceProcessingPreset(mode: Exclude<VoiceProcessingMode, 'custom'>): VoiceProcessingSettings {
  if (mode === 'raw') {
    return {
      mode,
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    }
  }
  if (mode === 'balanced') {
    return {
      mode,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: false,
    }
  }
  return {
    mode,
    echoCancellation: true,
    noiseSuppression: false,
    autoGainControl: true,
  }
}

export function readVoiceProcessingSettings(): VoiceProcessingSettings {
  try {
    const value = getLocalStorage()?.getItem(VOICE_PROCESSING_SETTINGS_KEY)
    if (!value) return defaultVoiceProcessingSettings()
    const parsed = JSON.parse(value) as Partial<VoiceProcessingSettings>
    return {
      mode: isVoiceProcessingMode(parsed.mode) ? parsed.mode : 'custom',
      echoCancellation: typeof parsed.echoCancellation === 'boolean'
        ? parsed.echoCancellation
        : defaultVoiceProcessingSettings().echoCancellation,
      noiseSuppression: typeof parsed.noiseSuppression === 'boolean'
        ? parsed.noiseSuppression
        : defaultVoiceProcessingSettings().noiseSuppression,
      autoGainControl: typeof parsed.autoGainControl === 'boolean'
        ? parsed.autoGainControl
        : defaultVoiceProcessingSettings().autoGainControl,
    }
  } catch {
    return defaultVoiceProcessingSettings()
  }
}

export function writeVoiceProcessingSettings(settings: VoiceProcessingSettings) {
  try {
    getLocalStorage()?.setItem(VOICE_PROCESSING_SETTINGS_KEY, JSON.stringify(settings))
  } catch {
    // Voice preferences are best-effort and should not block settings UI.
  }
}

export async function captureDisplay() {
  assertDisplayCaptureAvailable()
  return requestStreamWithTimeout(
    navigator.mediaDevices.getDisplayMedia({
      video: {
        frameRate: { ideal: 15, max: 30 },
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    }),
    'screen-timeout',
  ).catch((error: unknown) => {
    throw normalizeMediaError(error, 'screen')
  })
}

export function getSupportedVoiceConstraints(): VoiceConstraintSupport {
  const constraints = (globalThis.navigator?.mediaDevices?.getSupportedConstraints?.() ??
    {}) as ExtendedMediaTrackSupportedConstraints
  return {
    echoCancellation: Boolean(constraints.echoCancellation),
    noiseSuppression: Boolean(constraints.noiseSuppression),
    autoGainControl: Boolean(constraints.autoGainControl),
    channelCount: Boolean(constraints.channelCount),
    sampleRate: Boolean(constraints.sampleRate),
    sampleSize: Boolean(constraints.sampleSize),
    latency: Boolean(constraints.latency),
  }
}

export function recordVoiceConstraintSupport(support: VoiceConstraintSupport) {
  try {
    getLocalStorage()?.setItem(VOICE_CONSTRAINT_SUPPORT_KEY, JSON.stringify(support))
  } catch {
    // Storage is diagnostic-only and must not block media capture.
  }
}

export function readVoiceConstraintSupport(): VoiceConstraintSupport | null {
  try {
    const value = getLocalStorage()?.getItem(VOICE_CONSTRAINT_SUPPORT_KEY)
    if (!value) return null
    const parsed = JSON.parse(value) as Partial<VoiceConstraintSupport>
    return {
      echoCancellation: Boolean(parsed.echoCancellation),
      noiseSuppression: Boolean(parsed.noiseSuppression),
      autoGainControl: Boolean(parsed.autoGainControl),
      channelCount: Boolean(parsed.channelCount),
      sampleRate: Boolean(parsed.sampleRate),
      sampleSize: Boolean(parsed.sampleSize),
      latency: Boolean(parsed.latency),
    }
  } catch {
    return null
  }
}

export function normalizeMediaError(
  error: unknown,
  kind: 'microphone' | 'screen',
): VoiceMediaError {
  if (error instanceof VoiceMediaError) return error
  if (!(error instanceof DOMException)) {
    return new VoiceMediaError('unknown', 'Media capture failed', error)
  }
  if (kind === 'screen') {
    if (error.name === 'NotAllowedError') {
      return new VoiceMediaError('screen-permission-denied', 'Screen capture was denied', error)
    }
    if (error.name === 'NotFoundError' || error.name === 'NotReadableError') {
      return new VoiceMediaError('screen-unavailable', 'Screen capture is unavailable', error)
    }
    if (error.name === 'AbortError') {
      return new VoiceMediaError('screen-unavailable', 'Screen capture was cancelled', error)
    }
    return new VoiceMediaError('unknown', 'Screen capture failed', error)
  }
  if (error.name === 'NotAllowedError' || error.name === 'SecurityError') {
    return new VoiceMediaError('permission-denied', 'Microphone permission was denied', error)
  }
  if (error.name === 'NotFoundError') {
    return new VoiceMediaError('no-device', 'No microphone device was found', error)
  }
  if (error.name === 'NotReadableError') {
    return new VoiceMediaError('device-busy', 'Microphone is already in use', error)
  }
  if (error.name === 'OverconstrainedError' || error.name === 'ConstraintNotSatisfiedError') {
    return new VoiceMediaError('constraints-unsatisfied', 'Microphone constraints were not available', error)
  }
  if (error.name === 'AbortError') {
    return new VoiceMediaError('unknown', 'Microphone capture was cancelled', error)
  }
  return new VoiceMediaError('unknown', 'Microphone capture failed', error)
}

export function stopMediaStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop())
}

export function setAudioTracksMuted(stream: MediaStream | null, muted: boolean) {
  stream?.getAudioTracks().forEach((track) => {
    track.enabled = !muted
  })
}

export async function createVoiceInputProcessor(
  rawStream: MediaStream,
  initialSettings: VoiceDeviceSettings = readVoiceDeviceSettings(),
  options: VoiceInputProcessorOptions = {},
): Promise<VoiceInputProcessor> {
  const AudioContextConstructor = window.AudioContext
  if (!AudioContextConstructor) {
    return {
      stream: rawStream,
      updateSettings: () => {},
      close: () => stopMediaStream(rawStream),
    }
  }

  let context: AudioContext
  try {
    context = new AudioContextConstructor({ sampleRate: 48_000 })
  } catch {
    context = new AudioContextConstructor()
  }
  const source = context.createMediaStreamSource(rawStream)
  const highpass = context.createBiquadFilter()
  const compressor = context.createDynamicsCompressor()
  const inputGain = context.createGain()
  const levelGain = context.createGain()
  const gateGain = context.createGain()
  const analyser = context.createAnalyser()
  const destination = context.createMediaStreamDestination()
  const samples = new Float32Array(1024)
  let settings = normalizeVoiceDeviceSettings(initialSettings)
  let gateOpen = true
  let releaseTimer: number | null = null
  let intervalId: number | null = null
  let smoothedLevel = 0
  const rnnoiseNode = settings.rnnoiseSuppression
    ? await createRnnoiseNode(context)
    : null

  highpass.type = 'highpass'
  highpass.frequency.value = 90
  highpass.Q.value = 0.7
  compressor.threshold.value = -28
  compressor.knee.value = 12
  compressor.ratio.value = 2.4
  compressor.attack.value = 0.004
  compressor.release.value = 0.28
  analyser.fftSize = 1024
  analyser.smoothingTimeConstant = 0
  gateGain.gain.value = 1

  source.connect(highpass)
  highpass.connect(levelGain)
  levelGain.connect(analyser)
  if (rnnoiseNode) {
    highpass.connect(rnnoiseNode)
    rnnoiseNode.connect(compressor)
  } else {
    highpass.connect(compressor)
  }
  compressor.connect(inputGain)
  inputGain.connect(gateGain)
  gateGain.connect(destination)

  function applySettings(nextSettings: VoiceDeviceSettings) {
    settings = normalizeVoiceDeviceSettings(nextSettings)
    inputGain.gain.setTargetAtTime(settings.inputVolume / 100, context.currentTime, 0.025)
    levelGain.gain.setTargetAtTime(settings.inputVolume / 100, context.currentTime, 0.025)
    if (!settings.noiseGate) {
      gateOpen = true
      gateGain.gain.setTargetAtTime(1, context.currentTime, 0.025)
    }
  }

  function inputLevel() {
    analyser.getFloatTimeDomainData(samples)
    const rms = calculateRms(samples)
    const level = rmsToInputLevelPercent(rms)
    const smoothing = level > smoothedLevel ? 0.42 : 0.13
    smoothedLevel += (level - smoothedLevel) * smoothing
    return Math.round(smoothedLevel)
  }

  function openGate() {
    if (releaseTimer !== null) {
      window.clearTimeout(releaseTimer)
      releaseTimer = null
    }
    if (!gateOpen) {
      gateOpen = true
      gateGain.gain.setTargetAtTime(1, context.currentTime, 0.018)
    }
  }

  function scheduleGateClose() {
    if (releaseTimer !== null || !gateOpen) return
    releaseTimer = window.setTimeout(() => {
      releaseTimer = null
      gateOpen = false
      gateGain.gain.setTargetAtTime(GATE_ATTENUATED_GAIN, context.currentTime, 0.55)
    }, GATE_HOLD_MS)
  }

  function tickGate() {
    const level = inputLevel()
    options.onInputLevel?.(level)
    if (!settings.noiseGate) return
    const openThreshold = Math.max(5, settings.inputSensitivity - 10)
    const closeThreshold = Math.max(3, settings.inputSensitivity - 28)
    if (level >= openThreshold) {
      openGate()
      return
    }
    if (level < closeThreshold) scheduleGateClose()
  }

  applySettings(settings)
  intervalId = window.setInterval(tickGate, 40)

  return {
    stream: destination.stream,
    updateSettings: applySettings,
    close: () => {
      if (intervalId !== null) window.clearInterval(intervalId)
      if (releaseTimer !== null) window.clearTimeout(releaseTimer)
      rnnoiseNode?.destroy()
      stopMediaStream(rawStream)
      stopMediaStream(destination.stream)
      void context.close().catch(() => {})
    },
  }
}

export function calculateRms(samples: Float32Array) {
  if (samples.length === 0) return 0
  let total = 0
  for (const sample of samples) total += sample * sample
  return Math.sqrt(total / samples.length)
}

export function rmsToInputLevelPercent(rms: number) {
  if (!Number.isFinite(rms) || rms <= 0) return 0
  const db = 20 * Math.log10(Math.max(rms, 0.000_001))
  const percent = ((db - SILENCE_DB) / (SPEECH_REFERENCE_DB - SILENCE_DB)) * 100
  return Math.min(100, Math.max(0, Math.round(percent)))
}

export function screenTrackIsActive(stream: MediaStream) {
  return stream.getVideoTracks().some((track) => track.readyState === 'live' && !track.muted)
}

function assertMicrophoneCaptureAvailable() {
  if (!window.isSecureContext) {
    throw new VoiceMediaError(
      'insecure-context',
      'Microphone and screen capture require HTTPS or localhost',
    )
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new VoiceMediaError('media-unsupported', 'Browser media capture is unavailable')
  }
}

function assertDisplayCaptureAvailable() {
  if (!window.isSecureContext) {
    throw new VoiceMediaError(
      'insecure-context',
      'Microphone and screen capture require HTTPS or localhost',
    )
  }
  if (!navigator.mediaDevices?.getDisplayMedia) {
    throw new VoiceMediaError('screen-unavailable', 'Screen capture is unavailable')
  }
}

function getLocalStorage(): Storage | null {
  return typeof globalThis.localStorage === 'undefined' ? null : globalThis.localStorage
}

function isVoiceProcessingMode(value: unknown): value is VoiceProcessingMode {
  return value === 'balanced' || value === 'speech-stability' || value === 'raw' || value === 'custom'
}

export function buildAudioConstraints(
  support: VoiceConstraintSupport,
  settings: VoiceProcessingSettings = defaultVoiceProcessingSettings(),
  deviceSettings: VoiceDeviceSettings = defaultVoiceDeviceSettings(),
): MediaTrackConstraints {
  const audio: ExtendedMediaTrackConstraints = {}
  if (deviceSettings.inputDeviceId) {
    audio.deviceId = { exact: deviceSettings.inputDeviceId }
  }
  if (support.echoCancellation) audio.echoCancellation = { ideal: settings.echoCancellation }
  if (support.noiseSuppression) audio.noiseSuppression = { ideal: settings.noiseSuppression }
  if (support.autoGainControl) audio.autoGainControl = { ideal: settings.autoGainControl }
  if (support.channelCount) audio.channelCount = { ideal: 1 }
  if (support.sampleRate) audio.sampleRate = { ideal: 48_000 }
  if (support.sampleSize) audio.sampleSize = { ideal: 16 }
  if (support.latency) audio.latency = { ideal: 0.02 }
  return audio
}

function normalizeVoiceDeviceSettings(settings: Partial<VoiceDeviceSettings>): VoiceDeviceSettings {
  const defaults = defaultVoiceDeviceSettings()
  return {
    inputDeviceId: typeof settings.inputDeviceId === 'string' && settings.inputDeviceId
      ? settings.inputDeviceId
      : null,
    outputDeviceId: typeof settings.outputDeviceId === 'string' && settings.outputDeviceId
      ? settings.outputDeviceId
      : null,
    inputVolume: clampPercent(settings.inputVolume, defaults.inputVolume),
    outputVolume: clampPercent(settings.outputVolume, defaults.outputVolume),
    inputSensitivity: clampPercent(settings.inputSensitivity, defaults.inputSensitivity),
    noiseGate: typeof settings.noiseGate === 'boolean' ? settings.noiseGate : defaults.noiseGate,
    rnnoiseSuppression: typeof settings.rnnoiseSuppression === 'boolean'
      ? settings.rnnoiseSuppression
      : defaults.rnnoiseSuppression,
  }
}

async function createRnnoiseNode(context: AudioContext) {
  if (!context.audioWorklet || context.sampleRate !== 48_000) return null
  try {
    const { loadRnnoise, RnnoiseWorkletNode } = await import('@sapphi-red/web-noise-suppressor')
    const wasmBinary = await loadRnnoise({
      url: rnnoiseWasmPath,
      simdUrl: rnnoiseSimdWasmPath,
    })
    await context.audioWorklet.addModule(rnnoiseWorkletPath)
    return new RnnoiseWorkletNode(context, {
      wasmBinary,
      maxChannels: 1,
    }) as RnnoiseNode
  } catch {
    return null
  }
}

function clampPercent(value: unknown, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value)
    ? Math.min(100, Math.max(0, Math.round(value)))
    : fallback
}

function voiceDeviceOption(
  device: MediaDeviceInfo,
  index: number,
  kind: 'audioinput' | 'audiooutput',
): VoiceDeviceOption {
  const isDefault = device.deviceId === 'default'
  const fallback = kind === 'audioinput' ? `Microphone ${index + 1}` : `Speaker ${index + 1}`
  return {
    id: device.deviceId,
    label: device.label || (isDefault ? 'Default' : fallback),
    kind,
    isDefault,
  }
}

function requestStreamWithTimeout(
  request: Promise<MediaStream>,
  timeoutCode: VoiceMediaErrorCode,
) {
  let timedOut = false
  let timeoutId: number | null = null
  const timeout = new Promise<never>((_, reject) => {
    timeoutId = window.setTimeout(() => {
      timedOut = true
      reject(new VoiceMediaError(timeoutCode, 'Media permission prompt was not answered'))
    }, MEDIA_PERMISSION_TIMEOUT_MS)
  })
  request.then((stream) => {
    if (timeoutId !== null) window.clearTimeout(timeoutId)
    if (timedOut) stopMediaStream(stream)
  }).catch(() => {
    if (timeoutId !== null) window.clearTimeout(timeoutId)
    // The raced request handles rejection.
  })
  return Promise.race([request, timeout])
}
