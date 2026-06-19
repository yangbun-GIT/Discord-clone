const rawOrigin = process.env.DEPLOYMENT_ORIGIN ?? 'https://localhost:5173'
const requireTurn = process.env.REQUIRE_TURN === '1'
const allowInsecureLocal = process.env.ALLOW_INSECURE_LOCAL === '1'
const ignoreTlsErrors = process.env.DEPLOYMENT_IGNORE_TLS_ERRORS === '1'

if (ignoreTlsErrors) {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'
}

const origin = new URL(rawOrigin)
const isLocal =
  origin.hostname === 'localhost' ||
  origin.hostname === '127.0.0.1' ||
  origin.hostname === '[::1]' ||
  origin.hostname === '::1'

if (origin.protocol !== 'https:' && !(allowInsecureLocal && isLocal)) {
  throw new Error(
    'DEPLOYMENT_ORIGIN must be https for external deployment checks. ' +
      'Set ALLOW_INSECURE_LOCAL=1 only for local non-media checks.',
  )
}

if (ignoreTlsErrors && !isLocal) {
  throw new Error('DEPLOYMENT_IGNORE_TLS_ERRORS is only allowed for localhost checks')
}

const toHttpUrl = (pathname) => new URL(pathname, origin).toString()
const toWsUrl = (pathname) => {
  const ws = new URL(pathname, origin)
  ws.protocol = origin.protocol === 'https:' ? 'wss:' : 'ws:'
  return ws.toString()
}

async function fetchJson(pathname) {
  const response = await fetch(toHttpUrl(pathname))
  if (!response.ok) {
    throw new Error(`${pathname} returned HTTP ${response.status}`)
  }
  return response.json()
}

async function waitForGatewayHello() {
  const wsUrl = toWsUrl('/gateway')
  const socket = new WebSocket(wsUrl)

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      socket.close()
      reject(new Error('/gateway did not send HELLO before timeout'))
    }, 5000)

    socket.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(String(event.data))
        if (payload.op === 10) {
          clearTimeout(timeout)
          socket.close()
          resolve(true)
        }
      } catch {
        clearTimeout(timeout)
        socket.close()
        reject(new Error('/gateway sent a non-JSON message before HELLO'))
      }
    })

    socket.addEventListener('error', () => {
      clearTimeout(timeout)
      reject(new Error('/gateway WebSocket connection failed'))
    })
  })
}

const health = await fetchJson('/api/health')
const readiness = await fetchJson('/api/meta/voice/readiness')
await waitForGatewayHello()

const result = {
  origin: origin.toString(),
  secure_origin: origin.protocol === 'https:',
  tls_verification: ignoreTlsErrors ? 'ignored-for-local-check' : 'default',
  health_status: health.status ?? 'unknown',
  database_configured: Boolean(health.database?.configured),
  redis_configured: Boolean(health.redis?.configured),
  ice_server_count: Number(readiness.ice_server_count ?? 0),
  stun_configured: Boolean(readiness.stun_configured),
  turn_configured: Boolean(readiness.turn_configured),
  gateway_hello: true,
}

console.log(JSON.stringify(result, null, 2))

if (requireTurn && !result.turn_configured) {
  throw new Error('TURN is required for this check but readiness.turn_configured is false')
}

if (!result.turn_configured) {
  console.log('TURN is not configured. External TURN/NAT voice remains incomplete.')
}
