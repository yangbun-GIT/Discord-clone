import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import {
  buildAudioConstraints,
  calculateRms,
  normalizeMediaError,
  readVoiceDeviceSettings,
  readVoiceProcessingSettings,
  rmsToInputLevelPercent,
  VoiceMediaError,
  voiceProcessingPreset,
  writeVoiceDeviceSettings,
  writeVoiceProcessingSettings,
  type VoiceConstraintSupport,
} from './voiceMedia'

function domError(name: string) {
  return new DOMException('capture failed', name)
}

let originalLocalStorage: Storage | undefined

function installStorageDouble() {
  const values = new Map<string, string>()
  Object.defineProperty(globalThis, 'localStorage', {
    configurable: true,
    value: {
      clear: () => values.clear(),
      getItem: (key: string) => values.get(key) ?? null,
      key: (index: number) => Array.from(values.keys())[index] ?? null,
      removeItem: (key: string) => {
        values.delete(key)
      },
      setItem: (key: string, value: string) => {
        values.set(key, value)
      },
      get length() {
        return values.size
      },
    } satisfies Storage,
  })
}

beforeEach(() => {
  originalLocalStorage = globalThis.localStorage
  installStorageDouble()
})

afterEach(() => {
  if (originalLocalStorage) {
    Object.defineProperty(globalThis, 'localStorage', {
      configurable: true,
      value: originalLocalStorage,
    })
    return
  }
  Reflect.deleteProperty(globalThis, 'localStorage')
})

describe('normalizeMediaError', () => {
  it('keeps existing voice media errors', () => {
    const error = new VoiceMediaError('permission-timeout', 'timed out')

    expect(normalizeMediaError(error, 'microphone')).toBe(error)
  })

  it('maps microphone permission and device failures to typed codes', () => {
    expect(normalizeMediaError(domError('NotAllowedError'), 'microphone').code).toBe('permission-denied')
    expect(normalizeMediaError(domError('SecurityError'), 'microphone').code).toBe('permission-denied')
    expect(normalizeMediaError(domError('NotFoundError'), 'microphone').code).toBe('no-device')
    expect(normalizeMediaError(domError('NotReadableError'), 'microphone').code).toBe('device-busy')
    expect(normalizeMediaError(domError('OverconstrainedError'), 'microphone').code).toBe(
      'constraints-unsatisfied',
    )
  })

  it('maps screen capture failures separately from microphone failures', () => {
    expect(normalizeMediaError(domError('NotAllowedError'), 'screen').code).toBe('screen-permission-denied')
    expect(normalizeMediaError(domError('NotFoundError'), 'screen').code).toBe('screen-unavailable')
    expect(normalizeMediaError(domError('AbortError'), 'screen').code).toBe('screen-unavailable')
  })

  it('falls back to unknown for unclassified failures', () => {
    expect(normalizeMediaError(new Error('boom'), 'microphone').code).toBe('unknown')
    expect(normalizeMediaError(domError('UnknownError'), 'screen').code).toBe('unknown')
  })
})

describe('voice processing settings', () => {
  const fullSupport: VoiceConstraintSupport = {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    channelCount: true,
    sampleRate: true,
    sampleSize: true,
    latency: true,
  }

  it('defaults to speech-stability processing for sustained speech', () => {
    globalThis.localStorage.clear()

    expect(readVoiceProcessingSettings()).toEqual({
      mode: 'speech-stability',
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    })
  })

  it('persists user-selected processing toggles', () => {
    writeVoiceProcessingSettings({
      mode: 'custom',
      echoCancellation: false,
      noiseSuppression: true,
      autoGainControl: true,
    })

    expect(readVoiceProcessingSettings()).toEqual({
      mode: 'custom',
      echoCancellation: false,
      noiseSuppression: true,
      autoGainControl: true,
    })
  })

  it('provides named processing presets', () => {
    expect(voiceProcessingPreset('balanced')).toEqual({
      mode: 'balanced',
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: false,
    })
    expect(voiceProcessingPreset('speech-stability')).toEqual({
      mode: 'speech-stability',
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    })
    expect(voiceProcessingPreset('raw')).toEqual({
      mode: 'raw',
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    })
  })

  it('builds microphone constraints from browser support and user settings', () => {
    expect(buildAudioConstraints(fullSupport, {
      mode: 'custom',
      echoCancellation: false,
      noiseSuppression: true,
      autoGainControl: false,
    })).toMatchObject({
      echoCancellation: { ideal: false },
      noiseSuppression: { ideal: true },
      autoGainControl: { ideal: false },
      channelCount: { ideal: 1 },
      sampleRate: { ideal: 48000 },
      sampleSize: { ideal: 16 },
      latency: { ideal: 0.02 },
    })
  })

  it('persists device settings and clamps numeric controls', () => {
    writeVoiceDeviceSettings({
      inputDeviceId: 'mic-1',
      outputDeviceId: 'speaker-1',
      inputVolume: 130,
      outputVolume: -10,
      inputSensitivity: 41.4,
      noiseGate: false,
      rnnoiseSuppression: false,
    })

    expect(readVoiceDeviceSettings()).toEqual({
      inputDeviceId: 'mic-1',
      outputDeviceId: 'speaker-1',
      inputVolume: 100,
      outputVolume: 0,
      inputSensitivity: 41,
      noiseGate: false,
      rnnoiseSuppression: false,
    })
  })

  it('adds a selected microphone device to capture constraints', () => {
    expect(buildAudioConstraints(fullSupport, voiceProcessingPreset('balanced'), {
      inputDeviceId: 'mic-selected',
      outputDeviceId: null,
      inputVolume: 82,
      outputVolume: 100,
      inputSensitivity: 38,
      noiseGate: false,
      rnnoiseSuppression: false,
    })).toMatchObject({
      deviceId: { exact: 'mic-selected' },
    })
  })
})

describe('voice input level helpers', () => {
  it('calculates RMS for time-domain microphone samples', () => {
    expect(calculateRms(new Float32Array([0, 0, 0]))).toBe(0)
    expect(calculateRms(new Float32Array([1, -1, 1, -1]))).toBe(1)
  })

  it('maps RMS to a bounded Discord-like input meter percentage', () => {
    expect(rmsToInputLevelPercent(0)).toBe(0)
    expect(rmsToInputLevelPercent(0.0001)).toBe(0)
    expect(rmsToInputLevelPercent(0.08)).toBeGreaterThan(60)
    expect(rmsToInputLevelPercent(1)).toBe(100)
  })
})
