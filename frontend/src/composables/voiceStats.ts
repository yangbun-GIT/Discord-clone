import type { VoiceQualityStats } from '../types'

export interface VoiceStatsPeer {
  connection: RTCPeerConnection
}

type OutboundBytesSample = {
  bytes: number
  timestamp: number
}

export function createEmptyQualityStats(): VoiceQualityStats {
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

function average(values: number[]) {
  if (!values.length) return null
  return values.reduce((total, value) => total + value, 0) / values.length
}

export function createVoiceStatsCollector() {
  const previousOutboundBytes = new Map<string, OutboundBytesSample>()

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

  async function collect(peers: Map<number, VoiceStatsPeer>) {
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
    return nextStats
  }

  function reset() {
    previousOutboundBytes.clear()
  }

  return {
    collect,
    reset,
  }
}
