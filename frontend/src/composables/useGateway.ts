import { computed, onBeforeUnmount, ref } from 'vue'

import { useI18n } from '../i18n'
import { getNavigatorPlatform, getWebSocketUrl } from '../services/browserApi'

type GatewayStatus = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'offline' | 'error'

type GatewayEvent = {
  op: number
  d?: Record<string, unknown> | null
  s?: number | null
  t?: string | null
}

type GatewayDispatchHandler = (event: string, data: Record<string, unknown>) => void
type GatewayReconnectHandler = () => void | Promise<void>
type GatewayConnectOptions = {
  onDispatch?: GatewayDispatchHandler
  onReconnect?: GatewayReconnectHandler
}

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
const heartbeatAckTimer = ref<number | null>(null)
const reconnectTimer = ref<number | null>(null)
const dispatchHandler = ref<GatewayDispatchHandler | null>(null)
const reconnectHandler = ref<GatewayReconnectHandler | null>(null)
const currentToken = ref<string | null>(null)
let reconnectAttempts = 0
let manualDisconnect = false

const INITIAL_RECONNECT_DELAY_MS = 1000
const MAX_RECONNECT_DELAY_MS = 10000
const HEARTBEAT_ACK_TIMEOUT_MS = 5000

function clearHeartbeat() {
  if (heartbeatTimer.value !== null) {
    window.clearInterval(heartbeatTimer.value)
    heartbeatTimer.value = null
  }
  clearHeartbeatAckTimeout()
}

function clearHeartbeatAckTimeout() {
  if (heartbeatAckTimer.value !== null) {
    window.clearTimeout(heartbeatAckTimer.value)
    heartbeatAckTimer.value = null
  }
}

function clearReconnectTimer() {
  if (reconnectTimer.value !== null) {
    window.clearTimeout(reconnectTimer.value)
    reconnectTimer.value = null
  }
}

function send(payload: GatewayEvent) {
  if (socket.value?.readyState === WebSocket.OPEN) {
    socket.value.send(JSON.stringify(payload))
  }
}

function sendHeartbeat() {
  if (!socket.value || socket.value.readyState !== WebSocket.OPEN) return
  send({ op: 1 })
  clearHeartbeatAckTimeout()
  heartbeatAckTimer.value = window.setTimeout(() => {
    const staleSocket = socket.value
    if (!staleSocket || staleSocket.readyState !== WebSocket.OPEN) return
    status.value = 'reconnecting'
    staleSocket.close()
  }, HEARTBEAT_ACK_TIMEOUT_MS)
}

export function useGateway() {
  const { t } = useI18n()

  function startSocket(token: string, isReconnect: boolean) {
    status.value = isReconnect ? 'reconnecting' : 'connecting'
    const nextSocket = new WebSocket(getWebSocketUrl('/gateway'))
    socket.value = nextSocket

    nextSocket.addEventListener('message', (event) => {
      const payload = JSON.parse(event.data) as GatewayEvent
      if (payload.op === 10) {
        const interval = Number(payload.d?.heartbeat_interval ?? 30000)
        nextSocket.send(JSON.stringify({ op: 2, d: { token, os: getNavigatorPlatform(), library: 'vue' } }))
        clearHeartbeat()
        heartbeatTimer.value = window.setInterval(sendHeartbeat, interval)
      }
      if (payload.op === 11) {
        clearHeartbeatAckTimeout()
      }
      if (payload.t === 'READY') {
        status.value = 'connected'
        reconnectAttempts = 0
        if (isReconnect) {
          void reconnectHandler.value?.()
        }
      }
      if (payload.op === 0 && payload.t && payload.t !== 'READY' && payload.d) {
        dispatchHandler.value?.(payload.t, payload.d)
      }
    })

    nextSocket.addEventListener('error', () => {
      if (socket.value !== nextSocket || manualDisconnect) return
      status.value = 'error'
    })

    nextSocket.addEventListener('close', () => {
      if (socket.value !== nextSocket) return
      clearHeartbeat()
      socket.value = null
      if (manualDisconnect || !currentToken.value) {
        status.value = 'idle'
        return
      }
      scheduleReconnect()
    })
  }

  function scheduleReconnect() {
    if (!currentToken.value) {
      status.value = 'offline'
      return
    }
    clearReconnectTimer()
    status.value = 'reconnecting'
    const delay = Math.min(
      INITIAL_RECONNECT_DELAY_MS * (2 ** reconnectAttempts),
      MAX_RECONNECT_DELAY_MS,
    )
    reconnectAttempts += 1
    reconnectTimer.value = window.setTimeout(() => {
      reconnectTimer.value = null
      if (!currentToken.value || manualDisconnect) {
        status.value = 'offline'
        return
      }
      startSocket(currentToken.value, true)
    }, delay)
  }

  function connect(token: string, options: GatewayConnectOptions = {}) {
    currentToken.value = token
    dispatchHandler.value = options.onDispatch ?? null
    reconnectHandler.value = options.onReconnect ?? null
    if (socket.value && socket.value.readyState <= WebSocket.OPEN) {
      return
    }

    manualDisconnect = false
    clearReconnectTimer()
    startSocket(token, false)
  }

  function disconnect() {
    manualDisconnect = true
    clearHeartbeat()
    clearReconnectTimer()
    socket.value?.close()
    socket.value = null
    status.value = 'idle'
    currentToken.value = null
    dispatchHandler.value = null
    reconnectHandler.value = null
    reconnectAttempts = 0
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
      if (status.value === 'connected') return t('gateway.connected')
      if (status.value === 'connecting') return t('gateway.connecting')
      if (status.value === 'reconnecting') return t('gateway.reconnecting')
      if (status.value === 'offline') return t('gateway.offline')
      if (status.value === 'error') return t('gateway.error')
      return t('gateway.idle')
    }),
    connect,
    disconnect,
    updateVoiceState,
    sendVoiceSignal,
  }
}
