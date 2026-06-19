const MEDIA_PERMISSION_TIMEOUT_MS = 30_000
const VOICE_CONSTRAINT_SUPPORT_KEY = 'discord_clone_voice_constraint_support'
const VOICE_PROCESSING_SETTINGS_KEY = 'discord_clone_voice_processing_settings'

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
  echoCancellation: boolean
  noiseSuppression: boolean
  autoGainControl: boolean
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

export async function captureMicrophone() {
  assertMicrophoneCaptureAvailable()
  return requestStreamWithTimeout(
    navigator.mediaDevices.getUserMedia({
      audio: buildAudioConstraints(getSupportedVoiceConstraints(), readVoiceProcessingSettings()),
      video: false,
    }),
    'permission-timeout',
  ).catch((error: unknown) => {
    throw normalizeMediaError(error, 'microphone')
  })
}

export function defaultVoiceProcessingSettings(): VoiceProcessingSettings {
  return {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: false,
  }
}

export function readVoiceProcessingSettings(): VoiceProcessingSettings {
  try {
    const value = getLocalStorage()?.getItem(VOICE_PROCESSING_SETTINGS_KEY)
    if (!value) return defaultVoiceProcessingSettings()
    const parsed = JSON.parse(value) as Partial<VoiceProcessingSettings>
    return {
      echoCancellation: typeof parsed.echoCancellation === 'boolean'
        ? parsed.echoCancellation
        : true,
      noiseSuppression: typeof parsed.noiseSuppression === 'boolean'
        ? parsed.noiseSuppression
        : true,
      autoGainControl: typeof parsed.autoGainControl === 'boolean'
        ? parsed.autoGainControl
        : false,
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

export function buildAudioConstraints(
  support: VoiceConstraintSupport,
  settings: VoiceProcessingSettings = defaultVoiceProcessingSettings(),
): MediaTrackConstraints {
  const audio: ExtendedMediaTrackConstraints = {}
  if (support.echoCancellation) audio.echoCancellation = { ideal: settings.echoCancellation }
  if (support.noiseSuppression) audio.noiseSuppression = { ideal: settings.noiseSuppression }
  if (support.autoGainControl) audio.autoGainControl = { ideal: settings.autoGainControl }
  if (support.channelCount) audio.channelCount = { ideal: 1 }
  if (support.sampleRate) audio.sampleRate = { ideal: 48_000 }
  if (support.sampleSize) audio.sampleSize = { ideal: 16 }
  if (support.latency) audio.latency = { ideal: 0.02 }
  return audio
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
