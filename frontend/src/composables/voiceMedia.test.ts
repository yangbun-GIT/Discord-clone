import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import {
  buildAudioConstraints,
  normalizeMediaError,
  readVoiceProcessingSettings,
  VoiceMediaError,
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

  it('defaults to echo and noise processing without forcing auto gain', () => {
    globalThis.localStorage.clear()

    expect(readVoiceProcessingSettings()).toEqual({
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: false,
    })
  })

  it('persists user-selected processing toggles', () => {
    writeVoiceProcessingSettings({
      echoCancellation: false,
      noiseSuppression: true,
      autoGainControl: true,
    })

    expect(readVoiceProcessingSettings()).toEqual({
      echoCancellation: false,
      noiseSuppression: true,
      autoGainControl: true,
    })
  })

  it('builds microphone constraints from browser support and user settings', () => {
    expect(buildAudioConstraints(fullSupport, {
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
})
