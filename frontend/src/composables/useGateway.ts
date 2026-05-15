import { computed, onBeforeUnmount, ref } from 'vue'

type GatewayStatus = 'idle' | 'connecting' | 'connected' | 'disconnected'

type GatewayEvent = {
  op: number
  d?: Record<string, unknown> | null
  s?: number | null
  t?: string | null
}

type GatewayDispatchHandler = (event: string, data: Record<string, unknown>) => void

type VoiceStatePayload = {
  guild_id: number
  channel_id: number | null
  self_mute?: boolean
  self_deaf?: boolean
}

type VoiceSignalPayload = {
  channel_id: number
  target_user_id: number
  type: 'offer' | 'answer' | 'ice'
  description?: Record<string, unknown> | null
  candidate?: Record<string, unknown> | null
}

const socket = ref<WebSocket | null>(null)
const status = ref<GatewayStatus>('idle')
const heartbeatTimer = ref<number | null>(null)
const dispatchHandler = ref<GatewayDispatchHandler | null>(null)

function clearHeartbeat() {
  if (heartbeatTimer.value !== null) {
    window.clearInterval(heartbeatTimer.value)
    heartbeatTimer.value = null
  }
}

function send(payload: GatewayEvent) {
  if (socket.value?.readyState === WebSocket.OPEN) {
    socket.value.send(JSON.stringify(payload))
  }
}

export function useGateway() {
  function connect(token: string, options: { onDispatch?: GatewayDispatchHandler } = {}) {
    dispatchHandler.value = options.onDispatch ?? null
    if (socket.value && socket.value.readyState <= WebSocket.OPEN) {
      return
    }

    status.value = 'connecting'
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    socket.value = new WebSocket(`${protocol}://${window.location.host}/gateway`)

    socket.value.addEventListener('message', (event) => {
      const payload = JSON.parse(event.data) as GatewayEvent
      if (payload.op === 10) {
        const interval = Number(payload.d?.heartbeat_interval ?? 30000)
        send({ op: 2, d: { token, os: navigator.platform, library: 'vue' } })
        clearHeartbeat()
        heartbeatTimer.value = window.setInterval(() => send({ op: 1 }), interval)
      }
      if (payload.t === 'READY') {
        status.value = 'connected'
      }
      if (payload.op === 0 && payload.t && payload.t !== 'READY' && payload.d) {
        dispatchHandler.value?.(payload.t, payload.d)
      }
    })

    socket.value.addEventListener('close', () => {
      clearHeartbeat()
      status.value = 'disconnected'
      socket.value = null
    })
  }

  function disconnect() {
    clearHeartbeat()
    socket.value?.close()
    socket.value = null
    status.value = 'idle'
    dispatchHandler.value = null
  }

  function updateVoiceState(payload: VoiceStatePayload) {
    send({ op: 4, d: payload })
  }

  function sendVoiceSignal(payload: VoiceSignalPayload) {
    send({ op: 5, d: payload })
  }

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    status,
    statusLabel: computed(() => {
      if (status.value === 'connected') return 'Gateway online'
      if (status.value === 'connecting') return 'Connecting'
      if (status.value === 'disconnected') return 'Gateway offline'
      return 'Gateway idle'
    }),
    connect,
    disconnect,
    updateVoiceState,
    sendVoiceSignal,
  }
}
