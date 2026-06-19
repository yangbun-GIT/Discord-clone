import { describe, expect, it } from 'vitest'

import { normalizeMediaError, VoiceMediaError } from './voiceMedia'

function domError(name: string) {
  return new DOMException('capture failed', name)
}

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
